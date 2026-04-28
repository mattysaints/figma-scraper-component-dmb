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

Copia il file di esempio e inserisci il tuo token:

```bash
cp .env.example .env
# poi modifica .env e imposta FIGMA_ACCESS_TOKEN=...
```

In alternativa puoi esportare la variabile inline:

```bash
export FIGMA_ACCESS_TOKEN=your_figma_personal_access_token
```

> Senza `FIGMA_ACCESS_TOKEN` l'avvio di `uvicorn` fallisce con
> `ValidationError: FIGMA_ACCESS_TOKEN environment variable is required`.


---

## Running the API

```bash
uvicorn app.main:app --reload
```

Se la porta 8000 è già occupata:

```bash
uvicorn app.main:app --reload --port 8001
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

---

## Component Agent (dmbUi matching)

Oltre all'estrazione di stili, l'API include un agente che individua i
**componenti** presenti in un file Figma e li mappa sul catalogo dei componenti
`dmbUi` (es. `DxDynamicLocalizeTextView`, `InputViewField`, `DxPulsantiera`...).

### Come funziona

1. **Bootstrap del catalogo** a partire da una *showcase* Kotlin che già usa
   tutti i componenti `dmbUi`. Il parser estrae i nomi delle classi e ne deriva
   alias e proprietà attese.
2. **Estrazione** dei nodi Figma di tipo `COMPONENT`, `COMPONENT_SET`,
   `INSTANCE`, comprese **varianti** (`Variant=Value`) e
   `componentProperties`.
3. **Matching** in cascata:
   - alias/nome esatto → confidence `1.0`
   - tutti i token del candidato presenti come token del nome Figma → `0.7..0.9`
   - similarità + jaccard sui token → score smorzato (no falsi positivi)
   - tag con peso ridotto (solo come hint nei suggerimenti)
4. **Loop di apprendimento**: se un componente non viene riconosciuto, l'API
   restituisce i top-N suggerimenti. Tu confermi la mappatura una volta sola e
   il nome Figma viene salvato come **alias permanente** del componente
   `dmbUi`. La volta successiva il match è esatto.

### Endpoint principali

```
POST   /api/v1/catalog/components/bootstrap     # popola catalogo da Kotlin
GET    /api/v1/catalog/components               # lista catalogo
POST   /api/v1/catalog/components               # crea voce manuale
GET    /api/v1/catalog/components/{name}
PUT    /api/v1/catalog/components/{name}
DELETE /api/v1/catalog/components/{name}
POST   /api/v1/catalog/components/{name}/aliases  # conferma mapping (learning)

POST   /api/v1/figma/components                 # analisi componenti + match
```

### Quick start

```bash
# 1. Avvia l'API
uvicorn app.main:app --reload

# 2. Popola il catalogo dmbUi dallo showcase Kotlin (default: app/dmbComponent/showcaseUi.kt)
curl -X POST http://127.0.0.1:8000/api/v1/catalog/components/bootstrap \
  -H 'Content-Type: application/json' \
  -d '{"mode":"replace"}'

# 3. Analizza i componenti di un file Figma
curl -X POST http://127.0.0.1:8000/api/v1/figma/components \
  -H 'Content-Type: application/json' \
  -d '{
    "figma_url": "https://www.figma.com/design/FILE_KEY/Your-Design",
    "use_node_id": false,
    "confidence_threshold": 0.6,
    "include_unmatched": true
  }'

# 4. Quando un componente non viene riconosciuto, conferma manualmente
curl -X POST http://127.0.0.1:8000/api/v1/catalog/components/InputViewField/aliases \
  -H 'Content-Type: application/json' \
  -d '{"alias":"Text Field / Email"}'
```

### Esempio di risposta `/figma/components`

```json
{
  "file_key": "abc123",
  "node_id": null,
  "total_extracted": 3,
  "matched_count": 2,
  "unmatched_count": 1,
  "components": [
    {
      "extracted": {
        "figma_node_id": "10:42",
        "figma_name": "InputViewField",
        "figma_type": "INSTANCE",
        "variants": {},
        "properties": {"label": "Email", "disabled": "false"},
        "text_content": "Email",
        "width": 320, "height": 40, "children_count": 3
      },
      "best_match": {
        "dmbui_name": "InputViewField",
        "confidence": 1.0,
        "reason": "exact name match on 'InputViewField'"
      },
      "suggestions": [],
      "matched": true
    }
  ]
}
```

### Smoke test offline

```bash
python scripts/smoke_test.py
```

Esegue: parsing dello showcase Kotlin, popolamento del catalogo in-memory, e
matching su un documento Figma fittizio (no chiamate di rete).

---

## Web UI

Apri <http://127.0.0.1:8000/ui/> dopo aver avviato `uvicorn`.
La UI consente di:

- visualizzare il numero di componenti nel catalogo dmbUi
- bootstrappare il catalogo in modalità `merge` o `replace`
- creare manualmente un componente
- incollare un **link Figma** (anche con `?node-id=...&t=...`) e:
  - **Analizza componenti** → tabella con match dmbUi, confidence, varianti,
    `componentProperties`, e suggerimenti per i casi `unmatched`
  - **Estrai stili** → palette colori e text styles
- per ogni componente non matchato, scegliere dal menu un suggerimento
  (oppure digitare un nome canonico dmbUi) e cliccare **Conferma**: il nome
  Figma viene salvato come alias permanente del componente, così la prossima
  analisi sarà un match esatto (1.0).

Esempio di URL accettato (con `node-id`, basta abilitare `use_node_id=true`
nel form):

```
https://www.figma.com/design/ybz4qSWhVvRcEdd0OWFBvp/iDS---Moduli-e-template?node-id=6-230&p=f&t=1yHBM6LpEaRDioE5-0
```

