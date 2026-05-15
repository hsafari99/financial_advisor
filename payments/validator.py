"""Pure-data comparison of a parsed tax slip against accumulated paystub totals.

Claude Code extracts and interprets the slip PDF; this module handles only
the numeric diff and formatted output.
"""
from payments.accumulator import load

_FIELD_LABELS = {
    "employment_income": "Employment income",
    "federal_tax": "Federal tax",
    "provincial_tax": "Quebec tax (Box E)",
    "qpp": "QPP (Box B)",
    "ei": "EI (Box C)",
    "qpip": "QPIP (Box H)",
}

_TOTALS_MAP = {
    "employment_income": ("gross_pay", None),
    "federal_tax": ("deductions", "federal_tax"),
    "provincial_tax": ("deductions", "provincial_tax"),
    "qpp": ("deductions", "qpp"),
    "ei": ("deductions", "ei"),
    "qpip": ("deductions", "qpip"),
}


def validate(slip_data: dict, paystubs_path: str) -> None:
    """Compare slip_data (pre-parsed by Claude) against accumulated totals.

    slip_data keys: employment_income, federal_tax, provincial_tax, qpp, ei, qpip
    """
    data = load(paystubs_path)
    totals = data.get("totals", {})

    print("Tax Slip Validation")
    print("━" * 60)
    print(f"{'Field':<30} {'Slip':>12} {'YTD Stubs':>12} {'Delta':>10}")
    print("━" * 60)

    for field, label in _FIELD_LABELS.items():
        slip_val = slip_data.get(field, 0.0) or 0.0
        top_key, sub_key = _TOTALS_MAP[field]
        if sub_key is None:
            ytd_val = totals.get(top_key, 0.0) or 0.0
        else:
            ytd_val = (totals.get(top_key) or {}).get(sub_key, 0.0) or 0.0

        delta = slip_val - ytd_val
        mark = "✓" if abs(delta) < 1.0 else "✗"
        print(f"{label:<30} ${slip_val:>10,.2f} ${ytd_val:>10,.2f} ${delta:>8,.2f}  {mark}")

    print("━" * 60)
