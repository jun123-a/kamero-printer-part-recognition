# PV-ML-HPPK

HP LaserJet printer part identification system using YOLOv11 object detection. Upload a photo of a printer part; the system detects it, draws a bounding box, and returns the part name, serial number, and confidence score.


## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Quick Start (Docker)](#quick-start-docker)
- [Local Development Setup](#local-development-setup)
- [API Reference](#api-reference)
- [Database](#database)
- [Model](#model)
- [Part Classes](#part-classes)


## Overview

The system is built around three components:

1. **YOLO models** (`models/*.pt`) — trained to detect and classify 40 HP LaserJet printer part classes from images.
2. **FastAPI backend** (`app/main.py`) — receives image uploads, runs inference, annotates the image with bounding boxes, logs results to the database, and returns structured JSON.
3. **SQLite database** (`app/data/local.db`) — maps YOLO class IDs to real part names and serial numbers. Auto-created on first run.


## Project Structure

```
PV-ML-HPPK/
├── app/
│   ├── main.py          # FastAPI app — /predict, /feedback, /admin/clear-db
│   ├── database.py      # SQLAlchemy ORM models and DB engine
│   ├── seed_db.py       # Seeds 40 HP parts into DB on startup
│   ├── Dockerfile
│   └── static/
│       ├── index.html   # Frontend UI
│       ├── style.css
│       ├── hp_logo.png
│       └── woosong_logo.png
├── models/
│   └── *.pt             # YOLO weights 
├── notebooks/
│   └── *.ipynb          # YOLO jupyter notebooks 
├── scripts/
│   └── *.py             # Scripts used for dataset preparation 
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
└── readme.md
```

> `app/data/local.db` and `app/data/detection_images/` are created automatically on first run and are not tracked in git. Both are volume-mounted in Docker — data persists across container restarts.


## Requirements

- Python 3.10+

Key packages:

| Package | Purpose |
|---|---|
| `ultralytics` | YOLO model inference |
| `fastapi` | Web framework |
| `uvicorn` | ASGI server |
| `sqlalchemy` | ORM / SQLite |
| `pillow` | Image processing |


## Quick Start (Docker)

The recommended way to run the service. Requires Docker and Docker Compose.

**1. Place the model file**

```
models/*.pt
```

**2. Start the service**

```bash
docker compose up --build
```

On startup, the container automatically:
- Seeds the database with 40 HP part entries
- Starts the web server

**3. Open the app**

```
http://localhost:8000
```

To stop:

```bash
docker compose stop 
```

## Local Development Setup

**1. Clone and enter the repo**

```bash
git clone <repo-url>
cd PV-ML-HPPK
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / macOS
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Place the model file**

```
models/*.pt
```

**5. Initialize the database**

```bash
cd app
python seed_db.py
```

This creates `/data/local.db` and inserts 40 HP part entries. Safe to re-run — existing entries are skipped.

**6. Start the server**

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Open `http://localhost:8000`.


## API Reference

### `GET /`

Returns the frontend HTML page.


### `POST /detect`

Run inference on an uploaded image.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | Image file (JPEG, PNG, WEBP) |

**Response**

```json
{
  "image": "<base64-encoded JPEG with bounding boxes>"
  "conf": "[0.98, 0.45]"
  "cls": "[5RC00-67001, JC93-01467A]"
  "desc": "[HP LaserJet ADF Maintenance Kit, Right door switch assembly]"
}
```

| Field | Description |
|---|---|
| `image_base64` | Annotated image with bounding boxes (original if no detection) |
| `conf` | List of YOLO confidence score (all bounding boxes) |
| `cls` | List of part serial number |
| `message` | List of part description |

### `POST /classify`

Run inference on an uploaded image.

**Request** — `multipart/form-data`

| Field | Type | Description |
|---|---|---|
| `file` | file | Image file (JPEG, PNG, WEBP) |

**Response**

```json
{
  "image": "<base64-encoded JPEG with bounding boxes>"
  "conf": "[0.98, 0.45]"
  "cls": "[5RC00-67001, JC93-01467A]"
  "desc": "[HP LaserJet ADF Maintenance Kit, Right door switch assembly]"
}
```

| Field | Description |
|---|---|
| `image_base64` | Annotated image with bounding boxes (original if no detection) |
| `conf` | List of YOLO confidence score (Top 5) |
| `cls` | List of part serial number |
| `message` | List of part description |

### `DELETE /admin/clear-db`

Delete all detection history — logs, bounding boxes, and saved result images. HP part data is preserved.

```bash
curl -X DELETE http://localhost:8000/admin/clear-db
```

**Response**

```json
{
  "message": "Detection history cleared. 12 result image(s) deleted. Parts are preserved."
}
```


## Database

The SQLite database (`app/data/local.db`) contains four tables:

| Table | Description |
|---|---|
| `parts` | 40 HP part entries (class_id, part_name, serial_number) |
| `detection_logs` | One record per `/detect` call — image URL, JSON of {class, confidence, bbox} |
| `classification_logs` | One record per `/classify` call — image URL, JSON of {class, confidence} |

The database is created and seeded automatically on startup. No manual setup required.


## Model

`models/*.pt` are YOLO models trained on HP LaserJet printer part images. 

- Inference threshold: `conf=0.05` (low threshold to maximize recall)
- All detected bounding boxes are saved to DB; the highest-confidence box is shown in the UI
- Result images (with bounding boxes drawn) are saved to `app/data/detection_images/`


## Part Classes

The model detects 40 HP LaserJet part classes (IDs 0–39).

| Class ID | Part Name | Serial Number |
|---|---|---|
| 0 | SVC_HP LaserJet Fuser 220V Kit | 5PN77-67001 |
| 1 | SVC_HP LaserJet CYM Managed Imaging Drum | W9078-67001 |
| 2 | SVC_HP LaserJet Black Managed Imaging Drum | W9077-67001 |
| 3 | SVC_HP LaserJet Toner Collection Unit | 6SB85-67001 |
| 4 | Waste toner duct unit | JC96-13015A |
| 5 | SVC_HP LaserJet Trays 2-x Roller Kit | 5PN66-67001 |
| 6 | SVC_HP LaserJet Yellow Developer Unit | 5PN73-67003 |
| 7 | Hard disk 500GB SED | 933853-011 |
| 8 | HP LaserJet ADF Maintenance Kit | 5RC00-67001 |
| 9 | Main PCA (Formatter) | 6CF14-67011 |
| 10 | Laser scanner unit (LSU) | JC97-05149A |
| 11 | Control panel (10.1 inch) | 5QK42-60104 |
| 12 | SVC_T2 transfer assembly | 5PN80-67002 |
| 13 | Low Voltage Power Supply (LVPS), 220V | JC44-00150C |
| 14 | High Voltage Power Supply (HVPS) | JC44-00240C |
| 15 | SVC_HPLJ 300ipm300shtFlw DADFhighspdScnr | 5QK39-67002 |
| 16 | ADF Whole Unit Kit, Valiant A3 | 5QK08-67014 |
| 17 | Fuser drive board (FDB), 220V | JC44-00236C |
| 18 | SVC-Flat Cable, Faro SICB 50pin | 5QK08-67011 |
| 19 | SVC-Flat Cable, Faro SICB 68pin | 5QK08-67012 |
| 20 | FLAT CABLE-LSU | 5QK03-50003 |
| 21 | Exit unit | JC90-01856A |
| 22 | Right door assembly | JC95-02247A |
| 23 | Front cover assembly | 6ER04-61001 |
| 24 | Registration unit assembly | 8GS05-60128 |
| 25 | Registration sensor | 0604-001381 |
| 26 | Feed 2 sensor | 0604-001490 |
| 27 | Fuser, Exit drive assembly | JC93-01850A |
| 28 | Drum, ITB motor | JC31-00123C |
| 29 | Reservoir drive motor | JC93-01659A |
| 30 | Tray 3 empty sensor | 3SJ00-60110 |
| 31 | Duplex 1 motor | JC93-00336A |
| 32 | Toner dispense motor | SS216-80501 |
| 33 | CPR shutter motor | JC31-00078A |
| 34 | LVPS fan | JC31-00198A |
| 35 | FDB fan | JC31-00154A |
| 36 | LSU fan assembly | JC93-01019A |
| 37 | Right door switch assembly | JC93-01467A |
| 38 | Front door switch assembly | JC93-00466A |
| 39 | Outer environment sensor assembly | 5QJ90-40002 |
