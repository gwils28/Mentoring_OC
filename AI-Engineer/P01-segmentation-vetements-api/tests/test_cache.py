import numpy as np
from PIL import Image

from segvet import cache
from segvet.api import ApiError, CallInfo


class StubClient:
    """Renvoie une carte remplie de 6 (pantalon), ou une erreur pour les images listées."""

    def __init__(self, failing=()):
        self.failing, self.calls = set(failing), []

    def segment(self, path, max_side=512, as_png=False):
        self.calls.append((path.name, "png" if as_png else max_side))
        if path.name in self.failing:
            raise ApiError("HTTP 402 : crédits épuisés")
        width, height = Image.open(path).size
        return np.full((height, width), 6, np.uint8), CallInfo(200, 1, 0.5, 1000, {"x-compute-time": "0.3"})


def _images(tmp_path, n):
    paths = []
    for i in range(n):
        p = tmp_path / f"image_{i}.png"
        Image.new("RGB", (4, 3)).save(p)
        paths.append(p)
    return paths


def test_collect_caches_and_skips_already_done(tmp_path):
    images = _images(tmp_path, 3)
    client = StubClient()
    logs = cache.collect(client, images, root=tmp_path / "out")
    assert len(logs["jpeg512"]) == 3 and set(logs["png"]["status"]) == {200}
    assert cache.read_prediction(images[2], "png", root=tmp_path / "out").shape == (3, 4)
    cache.collect(client, images, root=tmp_path / "out")
    assert len(client.calls) == 6  # rien n'est redemandé à l'API


def test_variant_order_alternates_between_images(tmp_path):
    client = StubClient()
    cache.collect(client, _images(tmp_path, 2), root=tmp_path / "out")
    assert [side for _, side in client.calls] == [512, "png", "png", 512]


def test_failure_is_logged_and_retried_next_time(tmp_path):
    images = _images(tmp_path, 2)
    logs = cache.collect(StubClient(failing={"image_1.png"}), images, ("png",), root=tmp_path / "out")
    assert list(logs["png"]["status"]) == [200, "erreur"]
    logs = cache.collect(StubClient(), images, ("png",), root=tmp_path / "out")
    assert list(logs["png"]["status"]) == [200, 200]  # la dernière tentative l'emporte
