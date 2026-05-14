import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_value_over_time_chart(snapshots: list) -> go.Figure:
    fig = go.Figure()
    if not snapshots:
        fig.add_annotation(text="No historical data yet", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)
        return fig

    dates = [s["date"] for s in snapshots]
    accounts = set(k for s in snapshots for k in s.get("account_values_cad", {}).keys())
    colors = ["#4C72B0", "#DD8452", "#55A868", "#C44E52", "#8172B2"]

    for i, account in enumerate(sorted(accounts)):
        values = [s.get("account_values_cad", {}).get(account, None) for s in snapshots]
        fig.add_trace(go.Scatter(x=dates, y=values, name=account, mode="lines+markers", line=dict(color=colors[i % len(colors)])))

    totals = [s.get("total_value_cad") for s in snapshots]
    fig.add_trace(go.Scatter(x=dates, y=totals, name="Total", mode="lines+markers", line=dict(color="#2d2d2d", width=3)))
    fig.update_layout(title="Portfolio Value Over Time", yaxis_title="CAD", hovermode="x unified")
    return fig


def build_ticker_price_chart(ticker: str, snapshots: list, avg_cost: float) -> go.Figure:
    dates = [s["date"] for s in snapshots if ticker in s.get("prices", {})]
    prices = [s["prices"][ticker]["price"] for s in snapshots if ticker in s.get("prices", {})]
    currency = snapshots[-1]["prices"][ticker]["currency"] if snapshots else "CAD"

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=prices, name=ticker, mode="lines+markers"))
    if avg_cost:
        fig.add_hline(y=avg_cost, line_dash="dash", line_color="orange", annotation_text="Avg Cost", annotation_position="top right")
        fig.add_trace(go.Scatter(x=[], y=[], name="Avg Cost", line=dict(dash="dash", color="orange")))
    fig.update_layout(title=f"{ticker} Price Over Time ({currency})", yaxis_title=currency)
    return fig


def build_allocation_donut(actual: dict, target: dict) -> go.Figure:
    fig = make_subplots(rows=1, cols=2, specs=[[{"type": "domain"}, {"type": "domain"}]])
    fig.add_trace(go.Pie(labels=list(actual.keys()), values=list(actual.values()), name="Actual", hole=0.4), row=1, col=1)
    fig.add_trace(go.Pie(labels=list(target.keys()), values=list(target.values()), name="Target", hole=0.4), row=1, col=2)
    fig.update_layout(title="Allocation: Actual vs Target", annotations=[
        dict(text="Actual", x=0.18, y=0.5, font_size=14, showarrow=False),
        dict(text="Target", x=0.82, y=0.5, font_size=14, showarrow=False),
    ])
    return fig


def build_geo_bar(exposure: dict) -> go.Figure:
    sorted_items = sorted(exposure.items(), key=lambda x: x[1], reverse=True)
    fig = go.Figure(go.Bar(x=[v * 100 for _, v in sorted_items], y=[k for k, _ in sorted_items], orientation="h"))
    fig.update_layout(title="Geographic Exposure (%)", xaxis_title="%", yaxis_title="Region")
    return fig


def build_sector_bar(exposure: dict) -> go.Figure:
    sorted_items = sorted(exposure.items(), key=lambda x: x[1], reverse=True)
    fig = go.Figure(go.Bar(x=[v * 100 for _, v in sorted_items], y=[k for k, _ in sorted_items], orientation="h"))
    fig.update_layout(title="Sector Exposure (%)", xaxis_title="%", yaxis_title="Sector")
    return fig


def render_report(template_str: str, context: dict) -> str:
    from jinja2 import Environment
    env = Environment(autoescape=True)
    return env.from_string(template_str).render(**context)
