from unittest.mock import patch, MagicMock
import pytest
from portfolio.fetcher import fetch_live_prices, fetch_live_usdcad, fetch_historical_usdcad


def make_ticker_mock(price, currency):
    mock = MagicMock()
    mock.fast_info.last_price = price
    mock.fast_info.currency = currency
    return mock


@patch("portfolio.fetcher.yf.Ticker")
def test_fetch_live_prices_cad(mock_ticker):
    mock_ticker.return_value = make_ticker_mock(48.60, "CAD")
    result = fetch_live_prices(["VCN"])
    assert result == {"VCN": {"price": 48.60, "currency": "CAD"}}


@patch("portfolio.fetcher.yf.Ticker")
def test_fetch_live_prices_usd(mock_ticker):
    mock_ticker.return_value = make_ticker_mock(228.50, "USD")
    result = fetch_live_prices(["VTI"])
    assert result == {"VTI": {"price": 228.50, "currency": "USD"}}


@patch("portfolio.fetcher.yf.Ticker")
def test_fetch_live_usdcad(mock_ticker):
    mock_ticker.return_value = make_ticker_mock(1.3812, "USD")
    result = fetch_live_usdcad()
    assert result == 1.3812


@patch("portfolio.fetcher.yf.download")
def test_fetch_historical_usdcad_exact_date(mock_download):
    import pandas as pd
    mock_download.return_value = pd.DataFrame({"Close": [1.3750]})
    result = fetch_historical_usdcad("2026-05-14")
    assert result == 1.375


@patch("portfolio.fetcher.yf.download")
def test_fetch_historical_usdcad_weekend_fallback(mock_download):
    import pandas as pd
    mock_download.side_effect = [
        pd.DataFrame(),
        pd.DataFrame({"Close": [1.3800]}),
    ]
    result = fetch_historical_usdcad("2026-05-17")
    assert result == 1.38


@patch("portfolio.fetcher.yf.download")
def test_fetch_historical_usdcad_raises_after_max_lookback(mock_download):
    import pandas as pd
    mock_download.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="Could not fetch USD/CAD rate"):
        fetch_historical_usdcad("2026-05-14", max_lookback_days=7)
