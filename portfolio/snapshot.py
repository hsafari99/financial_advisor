import json
from pathlib import Path
from datetime import date


def save_snapshot(data: dict, reports_dir: Path) -> Path:
    report_date = data.get("date", date.today().isoformat())
    out_dir = Path(reports_dir) / report_date
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "snapshot.json"
    out_file.write_text(json.dumps(data, indent=2))
    return out_file


def load_all_snapshots(reports_dir: Path) -> list:
    snapshots = []
    for snapshot_file in sorted(Path(reports_dir).glob("*/snapshot.json")):
        snapshots.append(json.loads(snapshot_file.read_text()))
    return snapshots
