import plotly.graph_objects as go
from portfolio.renderer import (
    build_value_over_time_chart,
    build_ticker_price_chart,
    build_allocation_donut,
    build_geo_bar,
    build_sector_bar,
)


def test_value_over_time_single_snapshot():
    snapshots = [{"date": "2026-05-14", "total_value_cad": 50000.0, "account_values_cad": {"rrsp_user": 50000.0}}]
    fig = build_value_over_time_chart(snapshots)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_value_over_time_empty_snapshots():
    fig = build_value_over_time_chart([])
    assert isinstance(fig, go.Figure)


def test_ticker_price_chart():
    snapshots = [
        {"date": "2026-05-14", "prices": {"VTI": {"price": 219.45, "currency": "USD"}}},
        {"date": "2026-06-01", "prices": {"VTI": {"price": 228.50, "currency": "USD"}}},
    ]
    fig = build_ticker_price_chart("VTI", snapshots, avg_cost=221.92)
    assert isinstance(fig, go.Figure)
    assert any(t.name == "Avg Cost" for t in fig.data)


def test_allocation_donut():
    actual = {"VTI": 0.79, "XEC": 0.14, "VAB": 0.07}
    target = {"VTI": 0.75, "XEC": 0.18, "VAB": 0.07}
    fig = build_allocation_donut(actual, target)
    assert isinstance(fig, go.Figure)


def test_geo_bar():
    exposure = {"United States": 0.42, "Canada": 0.19, "Japan": 0.10}
    fig = build_geo_bar(exposure)
    assert isinstance(fig, go.Figure)


def test_sector_bar():
    exposure = {"Technology": 0.28, "Financials": 0.21, "Energy": 0.08}
    fig = build_sector_bar(exposure)
    assert isinstance(fig, go.Figure)


from jinja2 import Environment, FileSystemLoader

def test_report_contains_all_six_sections():
    env = Environment(loader=FileSystemLoader("portfolio/templates"), autoescape=True)
    tmpl = env.get_template("report.html")
    html = tmpl.render(
        report_date="2026-05-14", total_value_cad=87550.0, delta_cad=None,
        status="on_track", snapshot_count=1,
        allocation_donut_html="<p>donut</p>", geo_bar_html="<p>geo</p>",
        sector_bar_html="<p>sector</p>", value_chart_html="<p>value</p>",
        ticker_charts={}, accounts={}, plotlyjs=""
    )
    assert "Not professional financial advice" in html
    assert "Portfolio Summary" in html
    assert "Portfolio Value Over Time" in html
    assert "Per-Ticker Performance" in html
    assert "Allocation Drift" in html
    assert "Account Details" in html
    assert "Only one data point" in html
