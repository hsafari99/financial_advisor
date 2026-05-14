def compute_avg_cost(purchases: list) -> float:
    total_shares = sum(p["shares"] for p in purchases)
    total_cost = sum(p["shares"] * p["price"] for p in purchases)
    return round(total_cost / total_shares, 4)


def compute_account_value(holdings: list, prices: dict, usdcad_rate: float) -> float:
    total = 0.0
    for h in holdings:
        ticker = h["ticker"]
        price = prices[ticker]["price"]
        shares = h["total_shares"]
        if h["currency"] == "USD":
            total += shares * price * usdcad_rate
        else:
            total += shares * price
    return round(total, 2)


def compute_drift(actual: float, target: float) -> dict:
    drift = round(actual - target, 4)
    if abs(drift) > 0.10:
        status = "red"
    elif abs(drift) > 0.05:
        status = "amber"
    else:
        status = "green"
    return {"drift": drift, "status": status}


def compute_blended_exposure(ticker_weights: dict, etf_metadata: dict, key: str) -> dict:
    result = {}
    for ticker, weight in ticker_weights.items():
        for label, label_weight in etf_metadata[ticker][key].items():
            result[label] = round(result.get(label, 0.0) + weight * label_weight, 4)
    return result
