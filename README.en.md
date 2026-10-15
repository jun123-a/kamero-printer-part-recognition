# Kamero — Printer Part Recognition Web App

[한국어](readme.md) | **English**

[Frontend developer integration guide](docs/frontend-integration.en.md) — embedded E783 dataset tab, API contract, JSON format, local setup and model integration boundaries.

[Public dataset viewer](https://jun123-a.github.io/kamero-printer-part-recognition/?lang=en) · [한국어 화면](https://jun123-a.github.io/kamero-printer-part-recognition/)

A capstone project that detects printer parts in uploaded photos using an existing YOLO model, looks up part numbers and descriptions in SQLite, and displays the results in a browser.

This project connects the supplied Kamero frontend to [PV-ML-HPPK](https://github.com/snj0x03/PV-ML-HPPK). It is currently a **prototype for local use**.

## Features

- **E783 dataset database**: 31 document-mapped parts and Drive video metadata, kept separate from the legacy 40-class model catalogue. See the [setup and schema guide](docs/dataset-database.md). Open `/datasets` after importing your inventory.

- JPG/PNG uploads and real YOLO inference
- Linked selection between bounding boxes and the parts list, with zoom controls
- Warnings for predictions with confidence below 60%
- A searchable catalogue of 40 parts loaded from the server database
- ZIP export containing an annotated image, JSON, and CSV
- Detection results and result-image paths stored in SQLite
- Up to 20 recent recognition records stored in the browser
- User corrections included in the exported JSON

## How it works

```text
Browser: HTML / CSS / JavaScript
    │ POST /detect (original image)
    ▼
FastAPI → YOLO detection model → class IDs
    │                              │
    │                      SQLite part lookup
    ▼
Part numbers + descriptions + confidence + boxes + record ID
    │
    ▼
Interactive boxes, parts list, and result downloads
```

The preview is resized to a maximum long edge of 1,280 pixels, but the original file is sent to the server. The server applies EXIF orientation and validates the image format (JPG/PNG), file size (up to 10 MB), and pixel count (up to 40 megapixels).

## Quick start — Windows

The integration was verified on **Windows with Python 3.13**. It can run on a CPU without a GPU; processing time depends on the hardware.

Download or clone this repository, then run the following commands from the project directory:

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\start-kamero.cmd
```

Open **http://127.0.0.1:8000** in your browser. Do not open the HTML file directly.

The launcher uses the virtual environment in the project directory. Press Ctrl+C in the server window to stop the server. The database and initial parts catalogue are created automatically on startup.

Alternatively, start the server directly:

```powershell
.\.venv\Scripts\python.exe -m uvicorn main:app --app-dir app --host 127.0.0.1 --port 8000
```

Both model files are required at startup and are retained from the upstream repository:

- `models/best_v26_det.pt`: detection model used by the current frontend
- `models/best_v26_cls.pt`: classification model used by the existing `/classify` endpoint

## Project structure

```text
app/
  main.py                 # FastAPI, inference, database lookup, result storage
  database.py             # SQLite / SQLAlchemy tables
  seed_db.py              # Initial catalogue of 40 parts
  test_integration.py     # API integration tests
  static/
    index.html            # Page structure
    kamero.css            # Styles
    kamero.js             # Uploads, API calls, box selection, exports
    hp_logo.png
    woosong_logo.png
  data/                   # Generated database, images, settings; excluded from Git
models/                   # Existing trained models
notebooks/                # Existing training notebooks
scripts/                  # Existing data-processing scripts
requirements.txt          # Runtime dependencies
requirements-dev.txt      # Additional test dependencies
start-kamero.cmd           # Windows launcher
연결설명.md                # Detailed integration notes in Korean
```

## API

| Endpoint | Purpose |
|---|---|
| `GET /` | Serve the frontend |
| `GET /api/health` | Return server status and the detection model filename |
| `GET /api/models` | Return the supported recognition scope |
| `GET /api/parts` | Return the database parts catalogue |
| `POST /detect` | Detect parts in an image and store a record |
| `POST /classify` | Existing whole-image classification API; unused by the current frontend |
| `DELETE /admin/clear-db` | Delete detection/classification records and result images; preserve parts |

`/detect` accepts multipart form data with a `file` and an optional `printer_model`. The only supported scope is currently `All parts (printer compatibility unverified)`. Printer-specific filtering is not implemented.

Example response fields (illustrative values, not measured results):

```json
{
  "record_id": 1,
  "model_version": "best_v26_det.pt",
  "bbox_format": "cxcywh_normalized",
  "parts": [{
    "class_id": 0,
    "class_name": "0",
    "part_number": "5PN77-67001",
    "description": "SVC_HP LaserJet Fuser 220V Kit",
    "confidence": 0.92,
    "bbox_norm": [0.5, 0.5, 0.4, 0.2],
    "compatibility": []
  }]
}
```

Server boxes use normalized coordinates in the range 0–1: `[center x, center y, width, height]`. The frontend converts these to a top-left origin before drawing them. The `bbox_norm_xywh` field in exported JSON uses **top-left coordinates**.

The response also includes `image`, `conf`, `cls`, `desc`, and `bboxes` for compatibility with the existing API.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m unittest discover -s app -p test_integration.py
```

Completed checks:

- Four API integration tests passed: static assets/catalogue/scope, response contract and database persistence, invalid uploads, and real model inference
- JavaScript syntax and response-coordinate conversion checks passed
- All 40 catalogue entries were displayed in the browser
- A logo image was uploaded through the browser to the real model, and the no-detection message was displayed

Positive-detection coordinates and database mappings were tested with fixed model outputs. Accuracy on actual part photos and visual verification of their bounding boxes remain to be evaluated. These checks are not a model accuracy benchmark.

## Limitations and next steps

- Printer-specific compatibility data and filtering are not implemented.
- Swin classification and the YOLO crop → Swin pipeline are not implemented.
- The History tab reads browser storage; it does not retrieve server-side records.
- Corrections are included only in exported JSON. Server-side feedback storage and retraining are not implemented.
- Class-to-part mappings follow the upstream seed data and need verification against labelled photos.
- The detection threshold is set to 0.05. Low-confidence predictions require manual review.
- The existing administration API has no authentication. The default launcher binds to `127.0.0.1`; authentication and access controls are needed before exposing the service externally.
- The existing Docker configuration and training notebooks are retained but were not run as part of this integration work.

## Attribution and licensing

- Base code and trained models: [snj0x03/PV-ML-HPPK](https://github.com/snj0x03/PV-ML-HPPK)
- Frontend: adapted and separated from the Kamero HTML supplied for the project
- Integration changes: extended API responses, database-backed catalogue, original-image uploads, input validation, UI state handling, launcher, and integration tests
- The original MIT license and copyright notice are preserved in [LICENSE](LICENSE).
- The upstream README is preserved in [docs/upstream-readme.md](docs/upstream-readme.md). Use this README for the current integration's setup instructions.
- External dependencies such as Ultralytics, and assets such as logos and models, remain subject to their respective source terms.

For detailed integration notes in Korean, see [연결설명.md](연결설명.md).
