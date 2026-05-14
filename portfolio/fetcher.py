from datetime import date, timedelta
import yfinance as yf


def fetch_live_prices(tickers: list) -> dict:
    result = {}
    for ticker in tickers:
        info = yf.Ticker(ticker).fast_info
        result[ticker] = {"price": round(info.last_price, 4), "currency": info.currency}
    return result


def fetch_live_usdcad() -> float:
    return round(yf.Ticker("USDCAD=X").fast_info.last_price, 6)


def fetch_historical_usdcad(purchase_date: str, max_lookback_days: int = 7) -> float:
    d = date.fromisoformat(purchase_date)
    for offset in range(max_lookback_days + 1):
        check = d - timedelta(days=offset)
        data = yf.download(
            "USDCAD=X",
            start=check.isoformat(),
            end=(check + timedelta(days=1)).isoformat(),
            progress=False,
        )
        if not data.empty:
            return round(float(data["Close"].iloc[-1]), 6)
    raise ValueError(
        f"Could not fetch USD/CAD rate for {purchase_date}. "
        "Please add usd_cad_rate manually to portfolio.json."
    )
