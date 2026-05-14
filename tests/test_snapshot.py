import json
import pytest
from pathlib import Path
from portfolio.snapshot import save_snapshot, load_all_snapshots


def test_save_snapshot_creates_file(tmp_path):
    data = {"date": "2026-05-14", "total_value_cad": 50000.0}
    save_snapshot(data, reports_dir=tmp_path)
    saved = tmp_path / "2026-05-14" / "snapshot.json"
    assert saved.exists()
    assert json.loads(saved.read_text())["total_value_cad"] == 50000.0


def test_load_all_snapshots_empty(tmp_path):
    result = load_all_snapshots(reports_dir=tmp_path)
    assert result == []


def test_load_all_snapshots_returns_sorted(tmp_path):
    for d, val in [("2026-05-14", 50000.0), ("2026-06-01", 55000.0)]:
        (tmp_path / d).mkdir()
        (tmp_path / d / "snapshot.json").write_text(json.dumps({"date": d, "total_value_cad": val}))
    result = load_all_snapshots(reports_dir=tmp_path)
    assert [r["date"] for r in result] == ["2026-05-14", "2026-06-01"]
