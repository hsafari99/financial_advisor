import json
import os
import tempfile

_DEFAULT_PATH = os.path.join(os.path.dirname(__file__), "paystubs.json")


def load(path: str = _DEFAULT_PATH) -> dict:
    try:
        with open(path) as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save(data: dict, path: str = _DEFAULT_PATH) -> None:
    dir_ = os.path.dirname(path) or "."
    fd, tmp = tempfile.mkstemp(dir=dir_, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp, path)
    except Exception:
        os.unlink(tmp)
        raise


def _add_numeric(target: dict, source: dict) -> None:
    for key, val in source.items():
        if isinstance(val, dict):
            target.setdefault(key, {})
            _add_numeric(target[key], val)
        elif isinstance(val, (int, float)):
            target[key] = target.get(key, 0) + val


def recompute_totals(data: dict) -> dict:
    totals: dict = {
        "gross_pay": 0.0,
        "taxable_benefits": {},
        "deductions": {},
        "total_deductions": 0.0,
        "net_pay": 0.0,
    }
    for date_key, entry in data.items():
        if date_key == "totals":
            continue
        totals["gross_pay"] += entry.get("gross_pay", 0)
        totals["total_deductions"] += entry.get("total_deductions", 0)
        totals["net_pay"] += entry.get("net_pay", 0)
        _add_numeric(totals["taxable_benefits"], entry.get("taxable_benefits", {}))
        _add_numeric(totals["deductions"], entry.get("deductions", {}))

    data["totals"] = totals
    return data


def add_entry(data: dict, date: str, entry: dict) -> dict:
    data[date] = entry
    return recompute_totals(data)
