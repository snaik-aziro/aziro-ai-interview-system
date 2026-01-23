from datetime import datetime
import re

from src.utils.google_forms.form_api import (
    get_sheets_service,
    get_drive_service,
)

# Parent folder in Google Drive where result sheets live
FOLDER_ID = "1pcXw5Rn-2z3YBULkkbTmiPo91P9xxjRm"

ROUND_ORDER = ["L1", "L2", "L3", "L4", "L5"]


def _sanitize_drive_name(name: str) -> str:
    """
    Google Drive-safe name:
    - no backslashes
    - no newlines
    - no quotes
    """
    name = name.replace("\\", "/")
    name = name.replace("\n", " ").replace("\r", " ")
    name = re.sub(r"[\"']", "", name)
    return name.strip()


def _get_or_create_result_sheet(uid: str) -> str:
    drive = get_drive_service()
    sheets = get_sheets_service()

    # Sheet name must be Drive-safe
    name = _sanitize_drive_name(f"{uid}_results")

    query = (
        f"name = '{name}' and "
        f"'{FOLDER_ID}' in parents and "
        "mimeType = 'application/vnd.google-apps.spreadsheet' and "
        "trashed = false"
    )

    resp = drive.files().list(
        q=query,
        fields="files(id)",
    ).execute()

    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    # Create new spreadsheet
    sheet = sheets.spreadsheets().create(
        body={"properties": {"title": name}}
    ).execute()

    spreadsheet_id = sheet["spreadsheetId"]

    # Move it into the correct Drive folder
    drive.files().update(
        fileId=spreadsheet_id,
        addParents=FOLDER_ID,
        fields="id, parents",
    ).execute()

    _initialize_sheet(sheets, spreadsheet_id)
    return spreadsheet_id


def _initialize_sheet(sheets, spreadsheet_id: str):
    header = [[
        "UID",
        "Candidate Name",
        "Email",
        "Round",
        "Total Questions",
        "Correct Answers",
        "Score %",
        "Focus Violations",
        "Status",
        "Last Updated",
    ]]

    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A1:J1",
        valueInputOption="RAW",
        body={"values": header},
    ).execute()

    rows = [["", "", "", rnd, "", "", "", "", "", ""] for rnd in ROUND_ORDER]

    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A2:J6",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()


def save_round_result(
    uid: str,
    candidate_name: str,
    email: str,
    round_name: str,
    total_questions: int,
    correct_answers: int,
    score_percent: float,
    status: str,
    focus_violations: int = 0,
) -> str:
    """
    Update ONE fixed row per round (L1–L5).
    Idempotent.
    No append.
    No duplicates.
    """

    sheets = get_sheets_service()
    spreadsheet_id = _get_or_create_result_sheet(uid)

    sheet_name = "Sheet1"

    ROUND_TO_ROW = {
        "L1": 2,
        "L2": 3,
        "L3": 4,
        "L4": 5,
        "L5": 6,
    }

    if round_name not in ROUND_TO_ROW:
        return spreadsheet_id

    row_num = ROUND_TO_ROW[round_name]

    values = [[
        uid,
        candidate_name,
        email,
        round_name,
        total_questions,
        correct_answers,
        score_percent,
        focus_violations,
        status,
        datetime.now().isoformat(timespec="seconds"),
    ]]

    sheets.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_name}!A{row_num}:J{row_num}",
        valueInputOption="USER_ENTERED",
        body={"values": values},
    ).execute()

    return spreadsheet_id
