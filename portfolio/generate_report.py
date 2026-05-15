import json
import os
import tempfile
from datetime import date
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from portfolio.calculator import (
    compute_avg_cost,
    compute_blended_exposure,
    compute_drift,
)
from portfolio.fetcher import (
    fetch_historical_usdcad,
    fetch_live_prices,
    fetch_live_usdcad,
)
from portfolio.renderer import (
    build_allocation_donut,
    build_geo_bar,
    build_sector_bar,
    build_ticker_price_chart,
    build_value_over_time_chart,
)
from portfolio.snapshot import load_all_snapshots, save_snapshot

BASE_DIR = Path(__file__).parent
REPORTS_DIR = BASE_DIR.parent / "reports"
PORTFOLIO_PATH = BASE_DIR / "portfolio.json"
VALID_TICKERS = {"VTI", "VOO", "VCN", "XEF", "XEC", "VAB", "ZAG", "CASH.TO"}
CASH_ETFS = {"CASH.TO"}
CASH_TO_YIELD_PCT = 3.37


def _recompute_contributed(data: dict) -> None:
    for acc in data["accounts"].values():
        total = 0.0
        for holding in acc["holdings"]:
            for p in holding["purchases"]:
                if p["currency"] == "CAD":
                    total += p["shares"] * p["price"]
                elif p["currency"] == "USD":
                    total += p["shares"] * p["price"] * p.get("usd_cad_rate", 1.0)
        cash = acc.get("cash", {})
        total += cash.get("CAD", 0.0)
        total += cash.get("USD", 0.0) * cash.get("usd_cad_rate", 1.0)
        acc["total_contributed_cad"] = round(total, 2)


def update_cash(
    portfolio_path: Path = PORTFOLIO_PATH,
    account: str = None,
    cad: float = None,
    usd: float = None,
    usd_cad_rate: float = None,
):
    data = json.loads(Path(portfolio_path).read_text())

    if account not in data["accounts"]:
        raise ValueError(f"Unknown account: {account}. Valid: {list(data['accounts'].keys())}")

    cash = data["accounts"][account].setdefault("cash", {"CAD": 0.0, "USD": 0.0})
    if cad is not None:
        cash["CAD"] = round(cad, 2)
    if usd is not None:
        cash["USD"] = round(usd, 2)
    if usd_cad_rate is not None:
        cash["usd_cad_rate"] = usd_cad_rate

    _recompute_contributed(data)

    tmp = tempfile.NamedTemporaryFile(
        mode="w", dir=Path(portfolio_path).parent, delete=False, suffix=".tmp"
    )
    json.dump(data, tmp, indent=2)
    tmp.close()
    os.replace(tmp.name, portfolio_path)


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

    _recompute_contributed(data)

    tmp = tempfile.NamedTemporaryFile(
        mode="w", dir=Path(portfolio_path).parent, delete=False, suffix=".tmp"
    )
    json.dump(data, tmp, indent=2)
    tmp.close()
    os.replace(tmp.name, portfolio_path)


def generate_report(
    portfolio_path: Path = PORTFOLIO_PATH,
    targets_path: Path = BASE_DIR / "targets.json",
    metadata_path: Path = BASE_DIR / "etf_metadata.json",
    reports_dir: Path = REPORTS_DIR,
):
    portfolio = json.loads(Path(portfolio_path).read_text())
    targets = json.loads(Path(targets_path).read_text())
    etf_meta = json.loads(Path(metadata_path).read_text())

    all_tickers = {
        h["ticker"]
        for acc in portfolio["accounts"].values()
        for h in acc["holdings"]
    }

    if not all_tickers:
        print("No holdings found in portfolio.json. Add purchases first.")
        return None, None

    target_tickers = {t for acc in targets.values() for t in acc.keys()}
    prices_to_fetch = all_tickers | target_tickers
    # Try fetching all at once; fall back to individual fetches so a single
    # delisted/renamed ticker doesn't break the whole report.
    prices = {}
    for t in prices_to_fetch:
        try:
            prices.update(fetch_live_prices([t]))
        except Exception as e:
            print(f"WARNING: could not fetch price for {t}: {e}")
            prices[t] = {"price": None, "currency": "CAD"}
    usdcad_rate = fetch_live_usdcad()

    for acc in portfolio["accounts"].values():
        for holding in acc["holdings"]:
            if etf_meta.get(holding["ticker"], {}).get("currency") == "USD":
                for p in holding["purchases"]:
                    if "usd_cad_rate" not in p:
                        p["usd_cad_rate"] = fetch_historical_usdcad(p["date"])

    snapshots = load_all_snapshots(reports_dir)

    accounts_data = {}
    total_value_cad = 0.0
    consolidated_ticker_values = {}

    for acc_key, acc in portfolio["accounts"].items():
        if not acc["holdings"]:
            continue
        acc_target = targets.get(acc_key, {})
        holdings_data = {}
        acc_value_cad = 0.0

        for holding in acc["holdings"]:
            ticker = holding["ticker"]
            purchases = holding["purchases"]
            currency = etf_meta[ticker]["currency"]
            current_price = prices[ticker]["price"]
            if current_price is None:
                raise ValueError(f"No live price available for held ticker {ticker}.")
            avg_cost = compute_avg_cost(purchases)
            total_shares = sum(p["shares"] for p in purchases)

            if currency == "USD":
                value_cad = round(total_shares * current_price * usdcad_rate, 2)
            else:
                value_cad = round(total_shares * current_price, 2)

            acc_value_cad += value_cad
            consolidated_ticker_values[ticker] = consolidated_ticker_values.get(ticker, 0.0) + value_cad

            is_cash = ticker in CASH_ETFS
            holdings_data[ticker] = {
                "shares": total_shares,
                "avg_cost_per_share": avg_cost,
                "avg_cost_currency": currency,
                "current_price": current_price,
                "price_currency": currency,
                "gain_loss_per_share": round(current_price - avg_cost, 4) if not is_cash else None,
                "gain_loss_pct": round((current_price - avg_cost) / avg_cost * 100, 2) if not is_cash else None,
                "value_cad": value_cad,
                "is_cash_etf": is_cash,
                "yield_pct": CASH_TO_YIELD_PCT if is_cash else None,
            }

        drift_data = {}
        for ticker, target_pct in acc_target.items():
            actual_pct = holdings_data.get(ticker, {}).get("value_cad", 0.0) / acc_value_cad if acc_value_cad else 0.0
            drift_result = compute_drift(actual_pct, target_pct)
            rebalance_trade = None
            if drift_result["status"] == "red":
                delta_pct = target_pct - actual_pct
                delta_val = abs(delta_pct * acc_value_cad)
                action = "Buy" if delta_pct > 0 else "Sell"
                p_price = prices.get(ticker, {}).get("price")
                rate = usdcad_rate if etf_meta[ticker]["currency"] == "USD" else 1.0
                if p_price:
                    shares_needed = round(delta_val / (p_price * rate))
                    rebalance_trade = f"{action} ~{shares_needed} {ticker} (≈${delta_val:,.0f} CAD)"
                else:
                    rebalance_trade = f"{action} {ticker} (≈${delta_val:,.0f} CAD)"
            drift_data[ticker] = {**drift_result, "target": target_pct, "actual": actual_pct, "rebalance_trade": rebalance_trade}

        accounts_data[acc_key] = {
            "label": acc["label"],
            "contribution_room_remaining": acc.get("contribution_room_remaining", 0),
            "holdings": holdings_data,
            "drift": drift_data,
        }
        total_value_cad += acc_value_cad

    consolidated_weights = {t: v / total_value_cad for t, v in consolidated_ticker_values.items()} if total_value_cad else {}
    geo_exposure = compute_blended_exposure(consolidated_weights, etf_meta, "geography")
    sector_exposure = compute_blended_exposure(consolidated_weights, etf_meta, "sectors")

    delta_cad = None
    if snapshots:
        delta_cad = round(total_value_cad - snapshots[-1]["total_value_cad"], 2)

    has_red = any(
        d["status"] == "red"
        for acc in accounts_data.values()
        for d in acc["drift"].values()
    )
    status = "attention" if has_red else "on_track"

    account_values_cad = {
        k: sum(h["value_cad"] for h in v["holdings"].values())
        for k, v in accounts_data.items()
    }

    snapshot_data = {
        "date": date.today().isoformat(),
        "usdcad_rate": usdcad_rate,
        "prices": prices,
        "account_values_cad": account_values_cad,
        "total_value_cad": total_value_cad,
        "accounts": {
            acc_key: {
                "value_cad": sum(h["value_cad"] for h in acc["holdings"].values()),
                "holdings": {
                    t: {
                        "shares": h["shares"],
                        "avg_cost_per_share": h["avg_cost_per_share"],
                        "gain_loss_per_share": h["gain_loss_per_share"],
                        "gain_loss_pct": h["gain_loss_pct"],
                        "value_cad": h["value_cad"],
                    }
                    for t, h in acc["holdings"].items()
                },
            }
            for acc_key, acc in accounts_data.items()
        },
    }

    all_snapshots_with_today = snapshots + [snapshot_data]

    ticker_charts = {
        ticker: build_ticker_price_chart(
            ticker,
            all_snapshots_with_today,
            avg_cost=next(
                (acc["holdings"][ticker]["avg_cost_per_share"]
                 for acc in accounts_data.values() if ticker in acc["holdings"]),
                None,
            ),
        ).to_html(full_html=False, include_plotlyjs=False)
        for ticker in all_tickers
    }

    plotlyjs = build_value_over_time_chart([]).to_html(full_html=False, include_plotlyjs="cdn")

    flat_targets = {t: p for acc in targets.values() for t, p in acc.items()}

    env = Environment(loader=FileSystemLoader(str(BASE_DIR / "templates")), autoescape=True)
    tmpl = env.get_template("report.html")
    html = tmpl.render(
        report_date=date.today().isoformat(),
        total_value_cad=total_value_cad,
        delta_cad=delta_cad,
        status=status,
        snapshot_count=len(all_snapshots_with_today),
        allocation_donut_html=build_allocation_donut(consolidated_weights, flat_targets).to_html(full_html=False, include_plotlyjs=False),
        geo_bar_html=build_geo_bar(geo_exposure).to_html(full_html=False, include_plotlyjs=False),
        sector_bar_html=build_sector_bar(sector_exposure).to_html(full_html=False, include_plotlyjs=False),
        value_chart_html=build_value_over_time_chart(all_snapshots_with_today).to_html(full_html=False, include_plotlyjs=False),
        ticker_charts=ticker_charts,
        accounts=accounts_data,
        plotlyjs=plotlyjs,
    )

    snapshot_file = save_snapshot(snapshot_data, reports_dir)
    report_file = snapshot_file.parent / "report.html"
    report_file.write_text(html)

    return report_file, snapshot_data


if __name__ == "__main__":
    report_file, snapshot = generate_report()
    if report_file:
        total = snapshot["total_value_cad"]
        print(f"Report saved: {report_file}")
        print(f"Total portfolio value: ${total:,.2f} CAD")
