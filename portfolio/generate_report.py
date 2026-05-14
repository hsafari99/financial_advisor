import json
import tempfile
import os
from datetime import date
from pathlib import Path

VALID_TICKERS = {"VTI", "VOO", "VCN", "XEF", "XEC", "VAB", "ZAG", "CASH.TO"}
PORTFOLIO_PATH = Path(__file__).parent / "portfolio.json"


def add_purchase(
    portfolio_path: Path = PORTFOLIO_PATH,
    account: str = None,
    ticker: str = None,
    date: str = None,
    shares: float = None,
    price: float = None,
    currency: str = None,
    usd_cad_rate: float = None,
):
    if ticker not in VALID_TICKERS:
        raise ValueError(f"Unknown ticker: {ticker}. Valid: {sorted(VALID_TICKERS)}")
    if shares <= 0:
        raise ValueError("Shares must be positive")
    from datetime import date as date_cls
    if date_cls.fromisoformat(date) > date_cls.today():
        raise ValueError(f"Purchase date {date} is in the future")

    data = json.loads(Path(portfolio_path).read_text())

    if account not in data["accounts"]:
        raise ValueError(f"Unknown account: {account}. Valid: {list(data['accounts'].keys())}")

    purchase_entry = {"date": date, "shares": shares, "price": price, "currency": currency}
    if usd_cad_rate is not None:
        purchase_entry["usd_cad_rate"] = usd_cad_rate

    holdings = data["accounts"][account]["holdings"]
    for holding in holdings:
        if holding["ticker"] == ticker:
            holding["purchases"].append(purchase_entry)
            break
    else:
        holdings.append({"ticker": ticker, "purchases": [purchase_entry]})

    # Atomic write
    tmp = tempfile.NamedTemporaryFile(
        mode="w", dir=Path(portfolio_path).parent, delete=False, suffix=".tmp"
    )
    json.dump(data, tmp, indent=2)
    tmp.close()
    os.replace(tmp.name, portfolio_path)


def generate_report():
    pass  # implemented in Task 8
