import json
import os
from pathlib import Path

# -------------------------------------------------
# SESSION ID (MANDATORY)
# -------------------------------------------------
SESSION_ID = os.environ.get("AZIRO_SESSION_ID")
if not SESSION_ID:
    raise RuntimeError(
        "AZIRO_SESSION_ID not set. "
        "Start Streamlit with AZIRO_SESSION_ID=<port_or_name>"
    )

# -------------------------------------------------
# FORCE DEV STATE DIRECTORY (TEMP FIX)
# -------------------------------------------------
STATE_DIR = os.path.expanduser("~/.aziro_state")
Path(STATE_DIR).mkdir(parents=True, exist_ok=True)

STATE_FILE = os.path.join(STATE_DIR, f"state_{SESSION_ID}.json")


def load_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
