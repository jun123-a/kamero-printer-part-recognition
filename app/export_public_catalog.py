"""Export the explicitly approved public metadata snapshot, not the database."""
import json
from pathlib import Path
from database import SessionLocal
from dataset_api import datasets, parts, assets
from dataset_catalog import summary


def export():
    root = Path(__file__).resolve().parent.parent
    out = root / "docs"
    with SessionLocal() as db:
        listing = datasets(db)
        payload = {"datasets": listing["datasets"], "details": {}}
        for dataset in listing["datasets"]:
            did = dataset["id"]
            rows = []
            offset = 0
            while True:
                page = assets(did, None, offset, 200, db)
                rows.extend(page["assets"])
                if len(rows) >= page["total"]:
                    break
                offset += 200
            # Only fields displayed by the public viewer.
            public_rows = [{k: a[k] for k in ("name", "folder", "size_bytes", "source_url", "parts")} for a in rows]
            payload["details"][str(did)] = {"summary": summary(db, did), "parts": parts(did, db)["parts"], "assets": public_rows}
    (out / "catalogue.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    html = (root / "app/static/datasets.html").read_text(encoding="utf-8-sig")
    html = html.replace('href="/" data-en="← Recognition">← 인식 화면 / Recognition',
                        'href="https://github.com/jun123-a/kamero-printer-part-recognition" data-en="Source code">소스 코드')
    html = html.replace('href="/datasets"', 'href="./"').replace('href="/datasets?lang=en"', 'href="./?lang=en"')
    html = html.replace('/static/datasets.js?v=2', './datasets.js')
    html = html.replace('<script src=', '<script src="./public-data.js"></script><script src=', 1)
    (out / "index.html").write_text(html, encoding="utf-8")
    (out / "datasets.js").write_text((root / "app/static/datasets.js").read_text(encoding="utf-8"), encoding="utf-8")
    (out / ".nojekyll").touch()
    print(f"Exported {len(listing['datasets'])} dataset(s), {sum(len(d['assets']) for d in payload['details'].values())} video entries.")


if __name__ == "__main__":
    export()
