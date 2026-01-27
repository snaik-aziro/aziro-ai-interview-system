import json
import os
from pathlib import Path

# -------------------------------------------------
# SESSION ID
# -------------------------------------------------
SESSION_ID = (
    os.environ.get("AZIRO_SESSION_ID")
    or os.environ.get("UI_PORT")
    or "LOCAL"
)

# -------------------------------------------------
# STATE DIRECTORY (ENV-BASED, DEV SAFE)
# -------------------------------------------------
BASE_STATE_DIR = os.environ.get(
    "AZIRO_STATE_DIR",
    os.path.expanduser("~/.aziro_state")
)

STATE_DIR = Path(BASE_STATE_DIR)
STATE_DIR.mkdir(parents=True, exist_ok=True)

STATE_FILE = STATE_DIR / f"state_{SESSION_ID}.json"


def load_state():
    if not STATE_FILE.exists():
        return {}
    try:
        return json.loads(STATE_FILE.read_text())
    except Exception:
        return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))
