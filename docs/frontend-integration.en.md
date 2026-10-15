# Frontend Integration Guide — E783 Dataset

## What has been connected

The existing Kamero frontend now includes an **E783 dataset** tab alongside Recognize, Model parts (40), and History. The tab loads the existing dataset viewer inside a same-origin iframe. This reuses the working filtering, pagination, language switching, and Drive-link handling without duplicating its code or conflicting with the recognition page's DOM IDs.

The iframe loads only when the tab is first opened and stays mounted when switching tabs, preserving the selected part and page. Its initial URL is `/datasets?lang=en`. Users can open the viewer separately or follow the public snapshot link.

**This integration connects dataset browsing, not a newly trained recognition model.** The existing YOLO model still uses its legacy 40-class catalogue. E783 has a separate 31-part namespace. Selecting a part in the dataset viewer does not change the recognition model, upload scope, or prediction labels.

## Run and verify locally

Follow the repository README to install dependencies and start the app with `start-kamero.cmd`.

1. Open `http://127.0.0.1:8000/`.
2. Select **E783 dataset**.
3. Confirm that the viewer loads the registered dataset, parts and video entries.
4. Select Part_5. In the supplied inventory, this shows 20 file entries, including multi-part videos.
5. Switch to Recognize and back. The dataset selection should remain.

The owner's populated database contains 31 parts and 538 file entries. A fresh Git clone does **not** contain that database. Import an authorized inventory using:

```powershell
.venv\Scripts\python.exe app/import_dataset.py app/data/dataset_inventory.json
```

The importer backs up the existing database. Do not commit local DB files, credentials or model inference history.

## Architecture and data formats

```text
Local application
index.html → E783 tab → /datasets?lang=en
                       → datasets.js → /api/datasets/*
                                       → SQLAlchemy → SQLite local.db

Public GitHub Pages viewer
docs/index.html → docs/datasets.js → docs/public-data.js
                                  → docs/catalogue.json
```

- **SQLite is the local database**, managed with Python and SQLAlchemy.
- **JSON is the transport/export format**, not a replacement for the local database.
- Video bytes stay in Google Drive. The database and JSON store metadata and links.
- The public site is a static snapshot. It cannot perform recognition or query the owner's local server.
- After a local data update, regenerate the public snapshot with `python app/export_public_catalog.py` using the project environment, then publish the updated `docs/` files. This exports video links publicly.

## Files to work with

| File | Responsibility |
|---|---|
| app/static/index.html | Main frontend and embedded dataset tab |
| app/static/kamero.js | Main tab switching and lazy iframe loading |
| app/static/datasets.html | Reusable dataset viewer markup, Korean/English text |
| app/static/datasets.js | Dataset requests, filters, pagination and rendering |
| app/dataset_api.py | Read-only FastAPI endpoints |
| app/dataset_catalog.py | SQLAlchemy tables, import validation and summaries |
| app/catalogs/e783_parts.json | Document-derived 31-part mapping |
| app/export_public_catalog.py | Public JSON and viewer export |
| docs/public-data.js | Static JSON adapter for the public viewer |

Edit the source viewer under `app/static/`, then rerun the exporter. Editing only generated `docs/index.html` or `docs/datasets.js` will be overwritten by the next export.

## API contract

Use the same origin as the frontend. Discover dataset IDs from the list endpoint rather than hardcoding ID 1.

| Method and path | Response |
|---|---|
| GET /api/datasets | `{datasets: [{id, name, collected_at, mapping_source}]}` |
| GET /api/datasets/{id}/summary | Counts and data-preparation status |
| GET /api/datasets/{id}/parts | `{parts: [{part_no, svc_number, description}]}` |
| GET /api/datasets/{id}/assets | `{total, offset, limit, assets: [...]}` |

Asset query parameters:

- `part_no`: optional positive integer; matches any inferred part association.
- `offset`: nonnegative integer, default 0.
- `limit`: 1–200, default 50.

Unknown dataset IDs return HTTP 404. Invalid query parameters return HTTP 422. An unmatched part filter returns HTTP 200 with an empty asset list. An empty database returns `{datasets: []}`.

Example asset response (illustrative link):

```json
{
  "total": 20,
  "offset": 0,
  "limit": 50,
  "assets": [{
    "id": 123,
    "name": "5&6_1.mp4",
    "folder": "Part_5",
    "size_bytes": 123456,
    "source_url": "https://drive.google.com/file/d/EXAMPLE/view",
    "candidate_group": "opaque-filename-and-size-group",
    "content_verified": false,
    "parts": [
      {"part_no": 5, "evidence": "filename"},
      {"part_no": 6, "evidence": "filename"}
    ]
  }]
}
```

The public JSON has `datasets` and `details` keys. Each `details[String(id)]` contains `summary`, `parts`, and `assets`. Public asset records contain only `name`, `folder`, `size_bytes`, `source_url`, and `parts`. Do not require internal asset IDs or candidate-group fields when using the public snapshot.

## If replacing the iframe with native components

Use the same API contract. A minimal request sequence is:

```javascript
async function readJson(path, signal) {
  const response = await fetch(path, {signal});
  if (!response.ok) throw new Error("Request failed: " + response.status);
  return response.json();
}

const controller = new AbortController();
const {datasets} = await readJson("/api/datasets", controller.signal);
if (datasets.length) {
  const id = datasets[0].id;
  const [summary, catalogue] = await Promise.all([
    readJson(`/api/datasets/${id}/summary`, controller.signal),
    readJson(`/api/datasets/${id}/parts`, controller.signal)
  ]);
  const query = new URLSearchParams({part_no: "5", offset: "0", limit: "50"});
  const page = await readJson(`/api/datasets/${id}/assets?${query}`, controller.signal);
  // Render summary, catalogue.parts and page.assets.
}
// Abort on unmount or before replacing requests with a new filter selection.
```

Reset offset to zero when the part changes. Disable Previous at offset 0 and Next when `offset + limit >= total`. Ignore stale responses or abort superseded requests. Show loading, empty and error states. Render data with `textContent` or framework text bindings, not raw HTML.

For a separate frontend development server, proxy `/api` to the local FastAPI server. The backend currently has no cross-origin configuration. A same-origin reverse proxy is preferred for deployment; do not point a public frontend at `127.0.0.1`, which refers to each visitor's own device.

## Meaning of the dataset fields

- `part_no` is the document's 1-based Part No., not a YOLO class ID.
- SVC numbers are identifiers, not globally unique keys across datasets.
- Multiple parts can be associated with one video.
- Associations are inferred from filenames/folders; they are not verified visual labels.
- The 269 matching filename/size groups are duplicate candidates, not proven duplicates.
- `metadata_only`, `not_provided`, and `unassigned` mean videos have not been downloaded by this pipeline, annotations are absent, and a training split has not been assigned.

## Access and model handover

Public pages currently include source links. Drive permissions determine whether a visitor can open the actual videos. Only allow HTTPS Drive links in the viewer, and use `rel="noopener noreferrer"` for new tabs.

The current backend is a local prototype without authentication. Do not expose it directly as a team or production service: authentication, authorization and protection of administrative endpoints must be implemented first. The iframe is UI reuse, not an access-control boundary.

To connect a newly trained E783 model, the ML team must provide weights, class-ID-to-part mappings, preprocessing, inference code, dependency versions and evaluation results. Only then should recognition responses be mapped to E783 parts. Do not relabel existing predictions using this dataset's part numbers.
