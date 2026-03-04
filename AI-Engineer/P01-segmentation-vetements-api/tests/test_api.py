"""Le client est testé contre une fausse session HTTP : aucun appel réseau, aucun token réel."""

import numpy as np
import pytest
import requests
from PIL import Image

from segvet import api
from segvet.masks import label_map_to_results


class FakeClock:
    def __init__(self):
        self.now = 0.0
        self.sleeps = []

    def clock(self):
        return self.now

    def sleep(self, seconds):
        self.sleeps.append(seconds)
        self.now += seconds


class FakeResponse:
    def __init__(self, status, payload=None, headers=None):
        self.status_code, self._payload = status, payload
        self.headers = headers or {}
        self.text = "erreur"

    def json(self):
        return self._payload

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(self.status_code)


class FakeSession:
    """Rejoue une liste de réponses (ou d'exceptions) et enregistre les appels."""

    def __init__(self, replies):
        self.replies, self.calls, self.headers = list(replies), [], {}

    def post(self, url, data, headers, timeout):
        self.calls.append({"url": url, "headers": headers, "timeout": timeout, "size": len(data)})
        reply = self.replies.pop(0)
        if isinstance(reply, Exception):
            raise reply
        return reply


OK = FakeResponse(200, label_map_to_results(np.array([[0, 6]], np.uint8)), {"X-Compute-Time": "0.4"})


def make_client(replies, **kwargs):
    clock = FakeClock()
    session = FakeSession(replies)
    client = api.SegformerClient("hf_test", session=session, clock=clock.clock, sleep=clock.sleep, **kwargs)
    return client, session, clock


def test_token_is_sent_and_timeout_is_set():
    client, session, _ = make_client([OK], timeout=12)
    results, info = client.segment_bytes(b"jpeg")
    assert session.headers["Authorization"] == "Bearer hf_test"
    assert session.calls[0]["timeout"] == 12
    assert info.attempts == 1 and info.headers == {"x-compute-time": "0.4"}
    assert {r["label"] for r in results} == {"Background", "Pants"}


def test_retries_on_503_then_succeeds_with_backoff():
    client, session, clock = make_client([FakeResponse(503), FakeResponse(503), OK])
    _, info = client.segment_bytes(b"jpeg")
    assert info.attempts == 3
    assert clock.sleeps == [2.0, 4.0]


def test_retry_after_header_is_honoured():
    client, _, clock = make_client([FakeResponse(429, headers={"Retry-After": "7"}), OK])
    client.segment_bytes(b"jpeg")
    assert clock.sleeps == [7.0]


def test_timeout_is_retried():
    client, _, _ = make_client([requests.Timeout(), OK])
    assert client.segment_bytes(b"jpeg")[1].attempts == 2


@pytest.mark.parametrize("status", [401, 402, 403, 404])
def test_fatal_errors_are_not_retried(status):
    client, session, _ = make_client([FakeResponse(status), OK])
    with pytest.raises(api.ApiError, match=str(status)):
        client.segment_bytes(b"jpeg")
    assert len(session.calls) == 1


def test_gives_up_after_max_retries_without_leaking_token():
    client, session, _ = make_client([FakeResponse(503)] * 3, max_retries=2)
    with pytest.raises(api.ApiError, match="3 tentatives") as error:
        client.segment_bytes(b"jpeg")
    assert "hf_test" not in str(error.value)
    assert len(session.calls) == 3


def test_rate_limiter_never_exceeds_quota_in_any_minute():
    clock = FakeClock()
    limiter = api.RateLimiter(3, clock=clock.clock, sleep=clock.sleep)
    times = []
    for _ in range(7):
        limiter.wait()
        times.append(clock.now)
        clock.now += 1  # un appel dure 1 s
    for t in times:
        assert sum(t <= u < t + 60 for u in times) <= 3
    assert times[3] == 60.0


def test_rate_limiter_rejects_zero():
    with pytest.raises(ValueError):
        api.RateLimiter(0)


def test_prepare_image_shrinks_and_encodes_jpeg(tmp_path):
    path = tmp_path / "big.png"
    Image.new("RGB", (1200, 800), "red").save(path)
    data, size = api.prepare_image(path, max_side=512)
    assert size == (512, 341)
    assert data[:2] == b"\xff\xd8"  # signature JPEG


def test_segment_returns_map_at_original_size(tmp_path):
    path = tmp_path / "img.png"
    Image.new("RGB", (8, 4)).save(path)
    reply = FakeResponse(200, label_map_to_results(np.full((4, 8), 6, np.uint8)))
    client, _, _ = make_client([reply])
    label_map, _ = client.segment(path)
    assert label_map.shape == (4, 8) and (label_map == 6).all()


def test_load_token_reads_env_file(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    env = tmp_path / ".env"
    env.write_text("HF_TOKEN=hf_abc\n")
    assert api.load_token(env) == "hf_abc"


def test_missing_token_has_helpful_message(tmp_path, monkeypatch):
    monkeypatch.delenv("HF_TOKEN", raising=False)
    with pytest.raises(api.ApiError, match="HF_TOKEN"):
        api.load_token(tmp_path / ".env")


class FakeGetSession:
    def __init__(self, response):
        self.response, self.headers_seen = response, None

    def get(self, url, headers, timeout):
        self.headers_seen = headers
        return self.response


def test_check_token_returns_account_name():
    session = FakeGetSession(FakeResponse(200, {"name": "mentor"}))
    assert api.check_token("hf_test", session=session) == "mentor"
    assert session.headers_seen == {"Authorization": "Bearer hf_test"}


def test_check_token_rejects_invalid_token():
    with pytest.raises(api.ApiError, match="401"):
        api.check_token("hf_bad", session=FakeGetSession(FakeResponse(401)))


def test_segment_as_png_sends_original_file_untouched(tmp_path):
    path = tmp_path / "img.png"
    Image.new("RGB", (800, 600), "blue").save(path)
    reply = FakeResponse(200, label_map_to_results(np.zeros((600, 800), np.uint8)))
    client, session, _ = make_client([reply])
    client.segment(path, max_side=None, as_png=True)
    assert session.calls[0]["headers"] == {"Content-Type": "image/png"}
    assert session.calls[0]["size"] == path.stat().st_size


def test_segment_as_png_refuses_resizing(tmp_path):
    client, _, _ = make_client([])
    with pytest.raises(ValueError):
        client.segment(tmp_path / "img.png", max_side=512, as_png=True)


def test_latency_excludes_rate_limiter_wait_and_retries():
    clock = FakeClock()

    class SlowSession(FakeSession):
        def post(self, url, data, headers, timeout):
            clock.now += 0.5  # le serveur met 0,5 s à répondre
            return super().post(url, data, headers, timeout)

    session = SlowSession([OK, FakeResponse(503), OK])
    client = api.SegformerClient(
        "hf_test", max_per_minute=1, session=session, clock=clock.clock, sleep=clock.sleep
    )
    client.segment_bytes(b"jpeg")
    _, info = client.segment_bytes(b"jpeg")  # attend le limiteur, essuie une 503, puis réussit
    assert info.seconds == 0.5  # durée de la requête réussie seulement
    assert info.total_seconds > 60  # attentes et nouvelles tentatives comprises


def test_retry_after_is_capped():
    client, _, clock = make_client([FakeResponse(429, headers={"Retry-After": "3600"}), OK])
    client.segment_bytes(b"jpeg")
    assert clock.sleeps == [api.MAX_RETRY_AFTER]


def test_retry_after_as_http_date_is_understood():
    from datetime import UTC, datetime, timedelta
    from email.utils import format_datetime

    in_ten = format_datetime(datetime.now(UTC) + timedelta(seconds=10), usegmt=True)
    client, _, clock = make_client([FakeResponse(503, headers={"Retry-After": in_ten}), OK])
    client.segment_bytes(b"jpeg")
    assert 8 <= clock.sleeps[0] <= 10


def test_unexpected_200_body_is_an_api_error():
    client, _, _ = make_client([FakeResponse(200, {"error": "Model is loading"})])
    with pytest.raises(api.ApiError, match="inattendue"):
        client.segment_bytes(b"jpeg")
