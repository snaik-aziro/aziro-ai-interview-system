import os
import socket
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

BASE_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

CREDENTIALS_FILE = os.path.join(BASE_DIR, "credentials.json")

# ✅ Per-user token (prevents clashes between devs)
TOKEN_FILE = os.path.join(
    os.path.expanduser("~"),
    ".aziro_google_token.json"
)

SCOPES = [
    "https://www.googleapis.com/auth/forms.body",
    "https://www.googleapis.com/auth/forms.responses.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


def _get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("", 0))
        return s.getsockname()[1]


def get_credentials():
    creds = None

    # 1️⃣ Load token if exists
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # 2️⃣ If valid → DONE (MOST IMPORTANT PART)
    if creds and creds.valid:
        return creds

    # 3️⃣ Refresh expired token silently
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
        return creds

    # 4️⃣ Block OAuth in deploy
    if os.environ.get("AZIRO_DEPLOY") == "1":
        raise RuntimeError(
            "OAuth token missing or invalid in deploy. "
            "Generate token.json during dev and copy it."
        )

    # 5️⃣ DEV ONLY — OAuth browser flow (ONCE)
    flow = InstalledAppFlow.from_client_secrets_file(
        CREDENTIALS_FILE,
        SCOPES,
    )

    oauth_port = int(
        os.environ.get("AZIRO_OAUTH_PORT", _get_free_port())
    )

    creds = flow.run_local_server(
        port=oauth_port,
        prompt="consent",
        open_browser=True,
    )

    # 6️⃣ Save token permanently
    with open(TOKEN_FILE, "w") as token:
        token.write(creds.to_json())

    return creds
