"""Export only part information; never export video metadata."""
import json
from pathlib import Path


def export():
    root = Path(__file__).resolve().parent.parent
    mapping = json.loads((root / "app/catalogs/e783_parts.json").read_text(encoding="utf-8"))
    parts = [{key: row[key] for key in ("part_no", "svc_number", "description")} for row in mapping["parts"]]
    (root / "docs/catalogue.json").write_text(json.dumps({"parts": parts}, ensure_ascii=False), encoding="utf-8")
    print(f"Exported {len(parts)} parts; no video metadata.")


if __name__ == "__main__":
    export()
