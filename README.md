# Figma Style Extractor API

A FastAPI-based Python API that extracts **all text styles and colors** used in a Figma design.

You can extract:
- Styles from the **entire Figma file**
- Styles from a **specific node** (page, frame, component, etc.)

---

## Features

- Extracts:
  - Solid fill colors
  - Text styles (font family, size, weight, line height, letter spacing)
- Supports:
  - Full document extraction
  - Node-level extraction via `node-id`
- Strict typing (Pylance-friendly)
- Production-grade rate-limit handling (Figma API)

---

## Requirements

- Python **3.11+**
- A **Figma Personal Access Token**

> ⚠️ Note: Figma free accounts have **very limited API quotas**. <https://developers.figma.com/docs/rest-api/rate-limits/>

---

## Setup

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd figma-style-extractor
```

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

Windows
```bash
python -m venv .venv
```

Linux
```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

`FIGMA_ACCESS_TOKEN=your_figma_personal_access_token`


---

## Running the API

```bash
uvicorn app.main:app --reload
```

The API will be available at:
- API: <http://127.0.0.1:8000>
- Swagger UI: <http://127.0.0.1:8000/docs>

---

## Running the API

Endpoint

```bash
POST /api/v1/figma/analyze
```

Extract styles from a specific node
Set `use_node_id` to `true` and include `node-id` in the URL:

```json
{
  "figma_url": "https://www.figma.com/design/FILE_KEY/Your-Design-Name",
  "use_node_id": false
}
```

Response example

```json
{
  "colors": [
    { "hex": "#0F172A" },
    { "hex": "#FFFFFF" }
  ],
  "text_styles": [
    {
      "font_family": "Inter",
      "font_size": 16,
      "font_weight": 400,
      "line_height_px": 24,
      "letter_spacing": 0
    }
  ]
}
```

---

## Notes on Rate Limiting

- The API respects Figma’s `Retry-After` header
- If the wait time is too long, the API will fail fast and return:
    - HTTP `429`
    - A `Retry-After` header indicating when to retry

## Development Notes
- Designed with clean service boundaries
- Strict type checking enabled
- Easy to extend with:
    - Caching
    - Token-per-user support
    - Design token export formats