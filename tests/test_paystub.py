import pytest
from unittest.mock import patch, MagicMock


# ── extractor ──────────────────────────────────────────────────────────────

def test_extract_text_returns_nonempty_string():
    mock_page = MagicMock()
    mock_page.extract_text.return_value = "GAINS    Hres régu    4916.67\nR.R.Q.    321.68"
    mock_pdf = MagicMock()
    mock_pdf.__enter__ = lambda s: s
    mock_pdf.__exit__ = MagicMock(return_value=False)
    mock_pdf.pages = [mock_page]

    with patch("pdfplumber.open", return_value=mock_pdf):
        from payments.extractor import extract_text
        result = extract_text("dummy.pdf")

    assert isinstance(result, str)
    assert "4916.67" in result


# ── accumulator ────────────────────────────────────────────────────────────

def test_add_entry_new():
    from payments.accumulator import add_entry

    data = {}
    entry = {
        "employer": "Toon Boom",
        "pay_period": {"from": "2026-05-01", "to": "2026-05-15"},
        "gross_pay": 4916.67,
        "taxable_benefits": {"sick_leave": 328.61},
        "deductions": {"qpp": 321.68, "ei": 63.92, "other": {}},
        "total_deductions": 385.60,
        "net_pay": 4531.07,
    }
    result = add_entry(data, "2026-05-15", entry)

    assert "2026-05-15" in result
    assert result["totals"]["gross_pay"] == 4916.67
    assert result["totals"]["deductions"]["qpp"] == 321.68


def test_add_entry_overwrite():
    from payments.accumulator import add_entry

    entry1 = {
        "employer": "Toon Boom",
        "pay_period": {"from": "2026-05-01", "to": "2026-05-15"},
        "gross_pay": 4916.67,
        "taxable_benefits": {},
        "deductions": {"qpp": 321.68, "other": {}},
        "total_deductions": 321.68,
        "net_pay": 4595.0,
    }
    entry2 = {
        "employer": "Toon Boom",
        "pay_period": {"from": "2026-05-01", "to": "2026-05-15"},
        "gross_pay": 5000.0,
        "taxable_benefits": {},
        "deductions": {"qpp": 350.0, "other": {}},
        "total_deductions": 350.0,
        "net_pay": 4650.0,
    }

    data = add_entry({}, "2026-05-15", entry1)
    data = add_entry(data, "2026-05-15", entry2)

    assert data["2026-05-15"]["gross_pay"] == 5000.0
    assert data["totals"]["gross_pay"] == 5000.0
    assert data["totals"]["deductions"]["qpp"] == 350.0


def test_add_entry_multiple():
    from payments.accumulator import add_entry

    base = {
        "employer": "Toon Boom",
        "pay_period": {"from": "2026-05-01", "to": "2026-05-15"},
        "gross_pay": 4916.67,
        "taxable_benefits": {"sick_leave": 100.0},
        "deductions": {"qpp": 321.68, "ei": 63.92, "other": {}},
        "total_deductions": 385.60,
        "net_pay": 4531.07,
    }
    stub2 = {**base, "pay_period": {"from": "2026-06-01", "to": "2026-06-15"}}

    data = add_entry({}, "2026-05-15", base)
    data = add_entry(data, "2026-06-15", stub2)

    assert data["totals"]["gross_pay"] == pytest.approx(4916.67 * 2)
    assert data["totals"]["deductions"]["qpp"] == pytest.approx(321.68 * 2)
    assert data["totals"]["taxable_benefits"]["sick_leave"] == pytest.approx(100.0 * 2)


def test_recompute_totals_skips_totals_key():
    from payments.accumulator import recompute_totals

    data = {
        "2026-05-15": {
            "gross_pay": 1000.0,
            "taxable_benefits": {"sick_leave": 50.0},
            "deductions": {"qpp": 100.0, "other": {}},
            "total_deductions": 100.0,
            "net_pay": 900.0,
        },
        "totals": {
            "gross_pay": 9999.0,
            "taxable_benefits": {"sick_leave": 9999.0},
            "deductions": {"qpp": 9999.0, "other": {}},
            "total_deductions": 9999.0,
            "net_pay": 9999.0,
        },
    }
    result = recompute_totals(data)
    assert result["totals"]["gross_pay"] == 1000.0
    assert result["totals"]["deductions"]["qpp"] == 100.0
    assert result["totals"]["taxable_benefits"]["sick_leave"] == 50.0


def test_accumulator_atomic_write(tmp_path):
    from payments.accumulator import load, save

    path = str(tmp_path / "paystubs.json")
    data = {"2026-05-15": {"gross_pay": 1000.0}}
    save(data, path)
    loaded = load(path)
    assert loaded["2026-05-15"]["gross_pay"] == 1000.0


def test_load_missing_file(tmp_path):
    from payments.accumulator import load

    result = load(str(tmp_path / "nonexistent.json"))
    assert result == {}


# ── validator ──────────────────────────────────────────────────────────────

def test_validator_match(tmp_path, capsys):
    from payments.accumulator import save
    from payments.validator import validate

    paystubs_path = str(tmp_path / "paystubs.json")
    save({
        "totals": {
            "gross_pay": 60000.0,
            "taxable_benefits": {},
            "deductions": {
                "qpp": 3860.16, "ei": 767.04,
                "qpip": 253.68, "provincial_tax": 9402.36, "other": {}
            },
            "total_deductions": 14283.24,
            "net_pay": 45716.76,
        }
    }, paystubs_path)

    slip_data = {
        "employment_income": 60000.0,
        "provincial_tax": 9402.36,
        "qpp": 3860.16,
        "qpip": 253.68,
    }

    validate(slip_data, paystubs_path)

    captured = capsys.readouterr()
    assert "✓" in captured.out


def test_validator_mismatch(tmp_path, capsys):
    from payments.accumulator import save
    from payments.validator import validate

    paystubs_path = str(tmp_path / "paystubs.json")
    save({
        "totals": {
            "gross_pay": 60000.0,
            "taxable_benefits": {},
            "deductions": {
                "qpp": 3860.16, "ei": 767.04,
                "qpip": 253.68, "provincial_tax": 9402.36, "other": {}
            },
            "total_deductions": 14283.24,
            "net_pay": 45716.76,
        }
    }, paystubs_path)

    slip_data = {
        "employment_income": 60000.0,
        "provincial_tax": 9402.36,
        "qpp": 5000.00,  # mismatch
        "qpip": 253.68,
    }

    validate(slip_data, paystubs_path)

    captured = capsys.readouterr()
    assert "✗" in captured.out
