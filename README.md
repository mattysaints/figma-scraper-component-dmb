figma-scraper-api/
├─ app/
│  ├─ main.py              # App entry point
│  ├─ core/                # App-wide config & settings
│  │  ├─ __init__.py
│  │  └─ config.py
│  ├─ api/                 # API layer (routers)
│  │  ├─ __init__.py
│  │  └─ v1/
│  │     ├─ __init__.py
│  │     └─ health.py
│  ├─ schemas/             # Pydantic models (DTOs)
│  │  ├─ __init__.py
│  │  └─ health.py
│  ├─ services/            # Business logic
│  │  ├─ __init__.py
│  │  └─ health_service.py
│  └─ __init__.py
├─ .venv/
├─ requirements.txt
└─ README.md
