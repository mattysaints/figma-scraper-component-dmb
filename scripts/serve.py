"""Dev runner usabile come 'Run Script' in PyCharm: nessuna module mode richiesta."""
import os
import sys
from pathlib import Path

# Ensure project root is on sys.path so 'app' is importable regardless of CWD
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
# Also keep CWD aligned so uvicorn --reload watches the project tree
os.chdir(ROOT)

import uvicorn  # noqa: E402


def main() -> None:
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    reload = os.environ.get("RELOAD", "1") not in ("0", "false", "False")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        reload_dirs=[str(ROOT)] if reload else None,
        log_level=os.environ.get("LOG_LEVEL", "info"),
    )


if __name__ == "__main__":
    sys.exit(main() or 0)


