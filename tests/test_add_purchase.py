import json
import pytest
from pathlib import Path
from portfolio.generate_report import add_purchase


@pytest.fixture
def portfolio_file(tmp_path):
    data = {
        "accounts": {
            "rrsp_user": {"label": "RRSP (Hossein)", "contribution_room_remaining": 0, "holdings": []}
        }
    }
    f = tmp_path / "portfolio.json"
    f.write_text(json.dumps(data))
    return f


def test_add_purchase_appends_entry(portfolio_file):
    add_purchase(
        portfolio_path=portfolio_file,
        account="rrsp_user",
        ticker="VTI",
        date="2026-05-14",
        shares=50,
        price=219.45,
        currency="USD",
        usd_cad_rate=1.3812,
    )
    data = json.loads(portfolio_file.read_text())
    holdings = data["accounts"]["rrsp_user"]["holdings"]
    assert len(holdings) == 1
    assert holdings[0]["ticker"] == "VTI"
    assert holdings[0]["purchases"][0]["shares"] == 50


def test_add_purchase_appends_to_existing_ticker(portfolio_file):
    for price in [219.45, 228.10]:
        add_purchase(portfolio_file, "rrsp_user", "VTI", "2026-05-14", 50, price, "USD", 1.38)
    data = json.loads(portfolio_file.read_text())
    purchases = data["accounts"]["rrsp_user"]["holdings"][0]["purchases"]
    assert len(purchases) == 2


def test_add_purchase_invalid_ticker(portfolio_file):
    with pytest.raises(ValueError, match="Unknown ticker"):
        add_purchase(portfolio_file, "rrsp_user", "AAPL", "2026-05-14", 10, 150.0, "USD")


def test_add_purchase_invalid_account(portfolio_file):
    with pytest.raises(ValueError, match="Unknown account"):
        add_purchase(portfolio_file, "nonexistent", "VTI", "2026-05-14", 10, 219.45, "USD")


def test_add_purchase_negative_shares(portfolio_file):
    with pytest.raises(ValueError, match="Shares must be positive"):
        add_purchase(portfolio_file, "rrsp_user", "VTI", "2026-05-14", -5, 219.45, "USD")


def test_add_purchase_future_date(portfolio_file):
    with pytest.raises(ValueError, match="future"):
        add_purchase(portfolio_file, "rrsp_user", "VTI", "2099-01-01", 10, 219.45, "USD")
