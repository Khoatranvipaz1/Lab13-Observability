from app import metrics
from app.metrics import percentile


def test_percentile_basic() -> None:
    assert percentile([100, 200, 300, 400], 50) >= 100


def test_snapshot_includes_error_rate() -> None:
    metrics.TRAFFIC = 3
    metrics.ERRORS.clear()
    metrics.ERRORS["RuntimeError"] = 1
    result = metrics.snapshot()
    assert result["errors_total"] == 1
    assert result["error_rate_pct"] == 25.0
