import pytest

from segvet import cost


def test_required_rate_for_the_brief():
    assert cost.required_rate_per_minute(500_000, 30) == pytest.approx(11.574, abs=1e-3)


def test_serverless_cost_is_volume_times_time_times_price():
    assert cost.serverless_cost(500_000, 0.5, 0.0001) == pytest.approx(25.0)


def test_always_on_vs_batch():
    assert cost.dedicated_cost(720, 0.5) == 360
    hours = cost.batch_hours(500_000, 0.36, parallel=2)
    assert hours == pytest.approx(25.0)
    assert cost.dedicated_cost(hours, 0.5) == pytest.approx(12.5)
