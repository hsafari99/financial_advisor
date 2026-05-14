import pytest
from portfolio.calculator import (
    compute_avg_cost,
    compute_account_value,
    compute_drift,
    compute_blended_exposure,
)


def test_avg_cost_single_purchase():
    purchases = [{"shares": 50, "price": 219.45}]
    assert compute_avg_cost(purchases) == 219.45


def test_avg_cost_multiple_purchases():
    purchases = [
        {"shares": 50, "price": 219.45},
        {"shares": 20, "price": 228.10},
    ]
    expected = round((50 * 219.45 + 20 * 228.10) / 70, 4)
    assert compute_avg_cost(purchases) == expected


def test_account_value_cad_ticker():
    holdings = [{"ticker": "VCN", "total_shares": 100, "currency": "CAD"}]
    prices = {"VCN": {"price": 50.20, "currency": "CAD"}}
    result = compute_account_value(holdings, prices, usdcad_rate=1.38)
    assert result == pytest.approx(5020.0)


def test_account_value_usd_ticker_converted():
    holdings = [{"ticker": "VTI", "total_shares": 10, "currency": "USD"}]
    prices = {"VTI": {"price": 228.50, "currency": "USD"}}
    result = compute_account_value(holdings, prices, usdcad_rate=1.38)
    assert result == pytest.approx(10 * 228.50 * 1.38)


def test_drift_green():
    result = compute_drift(actual=0.77, target=0.75)
    assert result["status"] == "green"
    assert result["drift"] == pytest.approx(0.02)


def test_drift_amber():
    result = compute_drift(actual=0.82, target=0.75)
    assert result["status"] == "amber"


def test_drift_red():
    result = compute_drift(actual=0.86, target=0.75)
    assert result["status"] == "red"


def test_drift_red_triggers_above_10pct():
    result = compute_drift(actual=0.86, target=0.75)
    assert result["status"] == "red"
    assert result["drift"] == pytest.approx(0.11)


def test_drift_green_within_5pct():
    result = compute_drift(actual=0.77, target=0.75)
    assert result["status"] == "green"


def test_blended_exposure_geography():
    ticker_weights = {"VTI": 0.75, "VCN": 0.25}
    etf_metadata = {
        "VTI": {"geography": {"United States": 1.0}, "sectors": {}},
        "VCN": {"geography": {"Canada": 1.0}, "sectors": {}},
    }
    result = compute_blended_exposure(ticker_weights, etf_metadata, "geography")
    assert result == {"United States": 0.75, "Canada": 0.25}
