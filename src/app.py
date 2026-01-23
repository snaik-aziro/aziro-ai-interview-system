import sys
from pathlib import Path

# ================================================================
# PATH FIX
# ================================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from dotenv import load_dotenv

from src.utils.reports.l4_pdf_generator import generate_l4_pdf

load_dotenv()

import os

import time
import subprocess
import socket

import streamlit as st
import pandas as pd

# ================================================================
# ROUND DISPLAY LABELS (UI ONLY)
# ================================================================
ROUND_LABELS_BY_ROLE = {
    "python_entry": {
        "L1": "Aptitude",
        "L2": "Python",
        "L3": "Python Debugging",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "java_entry": {
        "L1": "Aptitude",
        "L2": "Java",
        "L3": "Java Debugging",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "js_entry": {
        "L1": "Aptitude",
        "L2": "JavaScript",
        "L3": "JS Debugging",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "python_qa": {
        "L1": "Aptitude",
        "L2": "Python",
        "L3": "QA & Testing",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "python_qa_linux": {
        "L1": "Linux",
        "L2": "Python",
        "L3": "QA & Testing",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "python_dev": {
        "L1": "Aptitude",
        "L2": "Python",
        "L3": "Python Dev",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "python_ai_ml": {
        "L1": "Aptitude",
        "L2": "Python",
        "L3": "AI / ML",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "java_aws": {
        "L1": "Aptitude",
        "L2": "Java",
        "L3": "AWS",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },

    "java_qa": {
        "L1": "Aptitude",
        "L2": "Java",
        "L3": "QA & Testing",
        "L4": "Coding Round",
        "L5": "Soft Skills",
    },
}

def get_round_label(role_key: str, round_key: str, domain: str | None):
    """
    Returns human-readable label for a round.
    UI-only helper.
    """

    base = ROUND_LABELS_BY_ROLE.get(role_key, {})

    # Coding is always fixed
    if round_key == "L4":
        return "Coding Round"

    # Domain selected → swap L5 / L6
    if domain and domain != "None":
        if round_key == "L5":
            return f"Domain – {domain.capitalize()}"
        if round_key == "L6":
            return "Soft Skills"

    return base.get(round_key, round_key)


# ================================================================
# VM IP (DO NOT TOUCH – WORKING)
# ================================================================
def get_vm_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip




# ================================================================
# STATE MANAGER
# ================================================================
from src.state_manager import load_state, save_state

_disk_state = load_state()

if "ui" not in st.session_state:
    st.session_state.ui = _disk_state.copy()

if "l4_process" not in st.session_state:
    st.session_state.l4_process = None


def commit_state():
    def sanitize(obj):
        if isinstance(obj, dict):
            return {k: sanitize(v) for k, v in obj.items() if not hasattr(v, "pid")}
        elif isinstance(obj, list):
            return [sanitize(v) for v in obj]
        return obj

    save_state(sanitize(st.session_state.ui))


# ================================================================
# IMPORTS
# ================================================================
from src.utils.google_forms.create_all_forms import create_all_google_forms
from src.utils.google_forms.evaluate_round import (
    evaluate_round_core,
    evaluate_l4_round,
)
#from src.utils.google_forms.save_results_to_sheet import save_round_result
from generate_candidate_test import run_candidate_test_generation_by_role

# ================================================================
# STREAMLIT CONFIG
# ================================================================
st.set_page_config(page_title="Aziro – Interview Automation", layout="wide")

# ================================================================
# BANNER
# ================================================================
BANNER_PATH = PROJECT_ROOT / "src" / "assets" / "aziro_banner.jpg"
if BANNER_PATH.exists():
    st.image(str(BANNER_PATH), use_container_width=True)

st.title("AI Interview Automation System")
ui = st.session_state.ui

# ================================================================
# ROLE CONFIG
# ================================================================
ROLE_OPTIONS = {
    "Python Entry (0–2 yrs)": "python_entry",
    "Java Entry (0–2 yrs)": "java_entry",
    "JavaScript Entry (0–2 yrs)": "js_entry",
    "Python QA / System / Linux (4+ yrs)": "python_qa_linux",
    "Python QA (4+ yrs)": "python_qa",
    "Python Developer (4+ yrs)": "python_dev",
    "Python + AI/ML (4+ yrs)": "python_ai_ml",
    "Java + AWS (5+ yrs)": "java_aws",
    "Java QA (5+ yrs)": "java_qa",
}

DOMAIN_OPTIONS = ["None", "Storage", "Virtualization", "Networking"]

# ================================================================
# DEFAULTS
# ================================================================
ui.setdefault("candidates", [])
# ------------------------------------------------
# Backward compatibility for existing candidates
# ------------------------------------------------
for cand in ui["candidates"]:
    if "tests_generated" not in cand:
        cand["tests_generated"] = bool(cand.get("forms"))
    if "email_sent" not in cand:
        cand["email_sent"] = False

ui.setdefault("evaluation_cache", {})
ui.setdefault("evaluation_selected_candidates", [])
ui.setdefault("evaluation_round", "L1")
ui.setdefault("eval_all_rounds", False)

# ================================================================
# RESET
# ================================================================
_, reset_col = st.columns([8, 1])
with reset_col:
    if st.button("🔄 Reset"):
        if st.session_state.l4_process:
            try:
                st.session_state.l4_process.terminate()
            except Exception:
                pass

        st.session_state.ui = {
            "candidates": [],
            "evaluation_selected_candidates": [],
            "evaluation_round": "L1",
            "eval_all_rounds": False,
        }
        commit_state()
        st.rerun()

def build_email_links(forms: dict) -> dict:
    email_links = {}

    for rnd, entry in forms.items():
        if not entry:
            continue

        if rnd == "L4":
            email_links[rnd] = entry
        else:
            email_links[rnd] = entry["responder_url"]

    return email_links


# ================================================================
# ADD CANDIDATE
# ================================================================
if len(ui["candidates"]) < 30:
    if st.button("➕ Add Candidate"):
        ui["candidates"].append({
            "name": "",
            "email": "",
            "role": list(ROLE_OPTIONS.values())[0],
            "domain": "None",
            "forms": None,
            "json_path": None,
            "tests_generated": False,  # 👈 NEW
            "email_sent": False,  # 👈 for resend UX
        })
        commit_state()

# ================================================================
# CANDIDATE ROWS
# ================================================================
from src.utils.email.send_assessment_email import send_assessment_email

for idx, cand in enumerate(ui["candidates"]):

    # 🔧 Added one more column for Email button
    cols = st.columns([3, 3, 3, 2, 1, 0.4])

    # -------- Name & Email --------
    cand["name"] = cols[0].text_input(
        "Name", cand["name"], key=f"name_{idx}"
    )
    cand["email"] = cols[1].text_input(
        "Email", cand["email"], key=f"email_{idx}"
    )

    # -------- Role --------
    role_label = cols[2].selectbox(
        "Role",
        options=list(ROLE_OPTIONS.keys()),
        index=list(ROLE_OPTIONS.values()).index(cand["role"]),
        key=f"role_{idx}",
    )
    cand["role"] = ROLE_OPTIONS[role_label]

    # -------- Domain --------
    cand["domain"] = cols[3].selectbox(
        "Domain (optional)",
        DOMAIN_OPTIONS,
        index=DOMAIN_OPTIONS.index(cand["domain"]),
        key=f"domain_{idx}",
    )

    # -------- Send / Resend Email Button --------
    btn_label = "📧 Resend Links" if cand.get("email_sent") else "📧 Send Links"

    if cols[4].button(btn_label, key=f"mail_{idx}"):

        if not cand.get("forms"):
            st.warning("⚠️ Generate tests before sending email.")
        else:
            round_labels = {
                rnd: get_round_label(
                    cand["role"],
                    rnd,
                    None if cand["domain"] == "None" else cand["domain"]
                )
                for rnd in cand["forms"]
            }

            try:
                email_links = build_email_links(cand["forms"])

                send_assessment_email(
                    candidate_name=cand["name"],
                    candidate_email=cand["email"],
                    company_name="Aziro Technologies Pvt Ltd",
                    round_links=email_links,
                    round_labels=round_labels,
                )

                # ✅ THIS IS THE IMPORTANT PART
                cand["email_sent"] = True
                commit_state()

                st.success(f"✅ Email sent to {cand['email']}")

            except Exception as e:
                st.error(f"❌ Email failed: {e}")

    # -------- Remove Candidate --------
    if cols[5].button("✕", key=f"remove_{idx}"):
        ui["candidates"].pop(idx)
        commit_state()
        st.rerun()

    commit_state()

# ================================================================
# GENERATE TESTS
# ================================================================
if st.button("🚀 Generate Tests for New Candidates"):
    pending = [c for c in ui["candidates"] if not c.get("tests_generated")]

    if not pending:
        st.info("✅ All candidates already have generated tests.")
        st.stop()

    progress = st.progress(0)
    total = len(pending)

    for i, cand in enumerate(pending, start=1):


        domain_selected = cand["domain"] != "None"

        uid, json_path = run_candidate_test_generation_by_role(
            full_name=cand["name"],
            email=cand["email"],
            role_key=cand["role"],
            domain=None if not domain_selected else cand["domain"].lower(),
        )

        # ---- Create Google Forms from JSON ----
        raw_forms = create_all_google_forms(json_path)

        # ---- FIX: L5 / L6 MAPPING BASED ON DOMAIN ----
        forms = {}

        forms["L1"] = raw_forms.get("L1")
        forms["L2"] = raw_forms.get("L2")
        forms["L3"] = raw_forms.get("L3")

        # L4 is added later (coding)
        # L5/L6 logic:
        if domain_selected:
            # Domain → L5, Soft Skills → L6
            forms["L5"] = raw_forms.get("L5")   # domain
            forms["L6"] = raw_forms.get("L6")   # soft skills
        else:
            # No domain → Soft Skills stays at L5
            forms["L5"] = raw_forms.get("L5")

        # ---- START L4 CODING SERVER ----
        port = 5001
        while True:
            try:
                s = socket.socket()
                s.bind(("127.0.0.1", port))
                s.close()
                break
            except OSError:
                port += 1

        proc = subprocess.Popen(
            [sys.executable, PROJECT_ROOT / "coding_round_l4" / "exam_server.py", str(port)],
            cwd=str(PROJECT_ROOT / "coding_round_l4"),
            env={
                **os.environ,
                "CANDIDATE_UID": uid,  # 🔥 KEY FIX
            }
        )

        st.session_state.setdefault("l4_processes", {})
        st.session_state.l4_processes[uid] = proc

        time.sleep(1)
        forms["L4"] = f"http://{get_vm_ip()}:{port}"

        cand["forms"] = forms
        cand["json_path"] = json_path

        # 🔥 ADD THIS (Step 3)
        cand["l4_result_path"] = str(
            PROJECT_ROOT / "coding_round_l4" / f"l4_result_{uid}.json"
        )

        cand["tests_generated"] = True
        commit_state()

    st.success("All candidate tests generated successfully")


# st.markdown("---")
# st.markdown("### Add More Candidates")

if st.button("➕ Add More Candidates"):
    ui["candidates"].append({
        "name": "",
        "email": "",
        "role": list(ROLE_OPTIONS.values())[0],
        "domain": "None",
        "forms": None,
        "json_path": None,
        "tests_generated": False,
        "email_sent": False,
    })
    commit_state()
    st.rerun()   # ✅ THIS IS THE FIX

# ================================================================
# TEST LINKS (COMPACT & CLEAN)
# ================================================================
if ui["candidates"]:
    st.markdown(
        "<h4 style='margin-bottom:4px;'>Generated Tests</h4>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<hr style='margin:4px 0 8px 0;'>",
        unsafe_allow_html=True
    )

    for cand in ui["candidates"]:
        if not cand.get("forms"):
            continue

        # Candidate name (tight spacing)
        st.markdown(
            f"<div style='font-weight:600; margin-bottom:2px;'>{cand['name']}</div>",
            unsafe_allow_html=True
        )

        # Test links with spacing
        links_html = []
        for lvl in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            entry = cand["forms"].get(lvl)
            if not entry:
                continue

            if lvl == "L4":
                url = entry
            elif isinstance(entry, dict):
                url = entry.get("responder_url")
            else:
                continue

            label = get_round_label(
                cand["role"],
                lvl,
                None if cand["domain"] == "None" else cand["domain"]
            )

            links_html.append(
                f"<a href='{url}' target='_blank' style='margin-right:12px;'>{label}</a>"
            )

        st.markdown(
            f"<div style='margin-bottom:8px;'>{''.join(links_html)}</div>",
            unsafe_allow_html=True
        )

# EVALUATION
# ================================================================
st.divider()
st.header("Evaluation")

candidate_map = {
    f"{c['name']} ({c['email']})": c
    for c in ui["candidates"]
    if c.get("json_path")
}

ui["evaluation_selected_candidates"] = st.multiselect(
    "Select Candidate(s)",
    options=list(candidate_map.keys()),
    default=ui.get("evaluation_selected_candidates", []),
    key="eval_candidates"
)

ui["eval_all_rounds"] = st.checkbox(
    "Evaluate ALL rounds",
    value=ui.get("eval_all_rounds", False),
    key="eval_all"
)

ui["evaluation_round"] = st.selectbox(
    "Select Round",
    ["L1", "L2", "L3", "L4", "L5", "L6"],
    index=["L1", "L2", "L3", "L4", "L5", "L6"].index(
        ui.get("evaluation_round", "L1")
    ),
    disabled=ui["eval_all_rounds"],
    key="eval_round"
)

commit_state()


# ================================================================
# RUN EVALUATION (FIXED FEEDBACK + SAFE GUARDS)
# ================================================================
if st.button("Evaluate Selected", key="eval_btn"):

    if not ui["evaluation_selected_candidates"]:
        st.warning("⚠️ Please select at least one candidate.")
        st.stop()

    evaluated_any = False

    for label in ui["evaluation_selected_candidates"]:
        cand = candidate_map[label]

        if not cand.get("json_path"):
            continue

        uid = cand["json_path"].split("/")[-1].replace(".json", "")
        ui["evaluation_cache"].setdefault(uid, {})

        rounds = (
            ["L1", "L2", "L3", "L4", "L5", "L6"]
            if ui["eval_all_rounds"]
            else [ui["evaluation_round"]]
        )

        for rnd in rounds:

            # -------- L4 (CODING) --------
            if rnd == "L4":
                res = evaluate_l4_round(
                    result_path=cand.get("l4_result_path"),
                    candidate_data={
                        "uid": uid,
                        "name": cand["name"],
                        "email": cand["email"],
                    }
                )



            elif rnd in cand.get("forms", {}):
                form_entry = cand["forms"].get(rnd)

                # 🚨 Skip if round not applicable / not generated
                if not isinstance(form_entry, dict):
                    continue

                form_id = form_entry.get("form_id")
                if not form_id:
                    continue

                res = evaluate_round_core(
                    form_id,
                    cand["json_path"]
                )



            # -------- NOT ATTEMPTED --------
            else:
                res = {
                    "uid": uid,
                    "round_name": rnd,
                    "total_questions": 0,
                    "correct_count": 0,
                    "score_percent": 0.0,
                    "status": "NO_RESPONSE",
                    "details": [],
                }

            ui["evaluation_cache"][uid][rnd] = res
            evaluated_any = True

    commit_state()

    if evaluated_any:
        st.success("✅ Evaluation completed successfully.")
    else:
        st.warning("⚠️ No rounds were evaluated.")


import csv
import os
from datetime import datetime
from src.utils.google_forms.form_api import get_drive_service

GOOGLE_DRIVE_RESULTS_ROOT = "1pcXw5Rn-2z3YBULkkbTmiPo91P9xxjRm"
from pathlib import Path
import os
import tempfile

BASE_TMP_DIR = os.environ.get(
    "AZIRO_TMP_DIR",
    tempfile.gettempdir() if os.name == "nt" else os.path.expanduser("~/.aziro_tmp")
)

LOCAL_TMP_DIR = Path(BASE_TMP_DIR) / "aziro_tmp_results"
LOCAL_TMP_DIR.mkdir(parents=True, exist_ok=True)


def safe_filename(text: str) -> str:
    return "_".join(text.strip().split())


def get_or_create_drive_folder(drive, name: str, parent_id: str) -> str:
    query = (
        f"name='{name}' and "
        f"mimeType='application/vnd.google-apps.folder' and "
        f"'{parent_id}' in parents and trashed=false"
    )

    res = drive.files().list(q=query, fields="files(id)").execute()
    files = res.get("files", [])

    if files:
        return files[0]["id"]

    folder = drive.files().create(
        body={
            "name": name,
            "mimeType": "application/vnd.google-apps.folder",
            "parents": [parent_id],
        },
        fields="id",
    ).execute()

    return folder["id"]

from googleapiclient.http import MediaFileUpload
import os
import csv
from datetime import datetime


def generate_candidate_csv_and_upload(uid: str, cand: dict, results: dict):
    """
    VM-ONLY IMPLEMENTATION (Ubuntu)
    - Generates CSV (unchanged logic)
    - Generates detailed PDF (ALL rounds + L4 deep dive)
    - Uploads both to SAME Drive folder
    """

    drive = get_drive_service()

    # ============================================================
    # Ensure UID is clean (Linux-safe)
    # ============================================================
    uid = os.path.basename(uid).replace(".json", "")

    # ============================================================
    # Google Drive folder structure
    # Results / <DATE> / <ROLE> /
    # ============================================================
    today_folder_name = datetime.now().strftime("%b_%d_%Y")

    date_folder_id = get_or_create_drive_folder(
        drive,
        today_folder_name,
        GOOGLE_DRIVE_RESULTS_ROOT
    )

    role_folder_id = get_or_create_drive_folder(
        drive,
        cand["role"],
        date_folder_id
    )

    # ============================================================
    # Local filesystem (VM)
    # ============================================================
    safe_candidate = safe_filename(cand["name"])
    local_dir = os.path.join(LOCAL_TMP_DIR, safe_candidate)
    os.makedirs(local_dir, exist_ok=True)

    filename = f"{safe_candidate}_{uid}.csv"
    csv_path = os.path.join(local_dir, filename)

    # ============================================================
    # Write CSV (UNCHANGED)
    # ============================================================
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "UID",
            "Candidate Name",
            "Email",
            "Round",
            "Total Questions",
            "Correct Answers",
            "Score %",
            "Status",
            "Last Updated",
        ])

        for rnd in ["L1", "L2", "L3", "L4", "L5", "L6"]:
            res = results.get(rnd, {})
            writer.writerow([
                uid,
                cand["name"],
                cand["email"],
                rnd,
                res.get("total_questions", 0),
                res.get("correct_count", 0),
                res.get("score_percent", 0.0),
                res.get("status", "NO_RESPONSE"),
                datetime.now().isoformat(timespec="seconds"),
            ])

    # ============================================================
    # Delete existing CSV in Drive (if any)
    # ============================================================
    query = (
        f"name='{filename}' and "
        f"'{role_folder_id}' in parents and trashed=false"
    )

    existing = drive.files().list(
        q=query,
        fields="files(id)"
    ).execute().get("files", [])

    for f in existing:
        drive.files().delete(fileId=f["id"]).execute()

    # ============================================================
    # Upload CSV
    # ============================================================
    uploaded_csv = drive.files().create(
        body={
            "name": filename,
            "parents": [role_folder_id],
        },
        media_body=csv_path,
        fields="id",
    ).execute()

    csv_file_id = uploaded_csv["id"]

    # ============================================================
    # PDF generation (ALL rounds + detailed L4)
    # ============================================================
    pdf_path = generate_l4_pdf(
        output_dir=local_dir,
        uid=uid,
        cand=cand,
        all_results=results,   # ✅ correct call-site change
    )

    pdf_name = os.path.basename(pdf_path)

    # ============================================================
    # Delete existing PDF in Drive (if any)
    # ============================================================
    query = (
        f"name='{pdf_name}' and "
        f"'{role_folder_id}' in parents and trashed=false"
    )

    existing_pdfs = drive.files().list(
        q=query,
        fields="files(id)"
    ).execute().get("files", [])

    for f in existing_pdfs:
        drive.files().delete(fileId=f["id"]).execute()

    # ============================================================
    # Upload PDF
    # ============================================================
    media = MediaFileUpload(pdf_path, mimetype="application/pdf")

    uploaded_pdf = drive.files().create(
        body={
            "name": pdf_name,
            "parents": [role_folder_id],
        },
        media_body=media,
        fields="id",
    ).execute()

    pdf_file_id = uploaded_pdf["id"]

    # ============================================================
    # Return IDs
    # ============================================================
    return {
        "csv_file_id": csv_file_id,
        "pdf_file_id": pdf_file_id,
    }




# ================================================================
# DISPLAY EVALUATION RESULTS (UI FEEDBACK)
# ================================================================
st.markdown("---")
st.header("Evaluation Results")

for label in ui["evaluation_selected_candidates"]:
    cand = candidate_map.get(label)
    if not cand or not cand.get("json_path"):
        continue

    uid = cand["json_path"].split("/")[-1].replace(".json", "")
    results = ui["evaluation_cache"].get(uid)

    if not results:
        continue

    name_col, btn_col = st.columns([6, 3])

    with name_col:
        st.subheader(f"{cand['name']} ({cand['email']})")

    with btn_col:
        if st.button(
                "📄 Generate Report",
                key=f"csv_btn_{uid}"
        ):
            ids = generate_candidate_csv_and_upload(
                uid=uid,
                cand=cand,
                results=results
            )

            ui["evaluation_cache"].setdefault(uid, {})

            # Store CSV + PDF file IDs
            ui["evaluation_cache"][uid]["csv_file_id"] = ids.get("csv_file_id")
            ui["evaluation_cache"][uid]["pdf_file_id"] = ids.get("pdf_file_id")

            commit_state()

            st.success("✅ CSV & PDF generated and uploaded to Google Drive")
    pdf_file_id = results.get("pdf_file_id")
    if pdf_file_id:
        pdf_url = f"https://drive.google.com/file/d/{pdf_file_id}/view"
        st.markdown(f"📑 [Open L4 Coding Report (PDF)]({pdf_url})")

    # 🔗 OPEN CSV LINK (THIS IS THE FIX YOU ASKED)
    csv_file_id = results.get("csv_file_id")
    if csv_file_id:
        csv_url = f"https://drive.google.com/file/d/{csv_file_id}/view"
        st.markdown(f"🔗 [Open CSV Results]({csv_url})")

    # ---- Per-round details ----
    for rnd in ["L1", "L2", "L3", "L4", "L5", "L6"]:
        res = results.get(rnd)
        if not res:
            continue

        score = res.get("score_percent", 0.0)
        status = res.get("status", "NO_RESPONSE")

        label_name = get_round_label(
            cand["role"],
            rnd,
            None if cand["domain"] == "None" else cand["domain"]
        )

        with st.expander(f"{label_name} ({rnd}) | {score}% | {status}"):
            st.json({
                "Total Questions": res.get("total_questions", 0),
                "Correct Answers": res.get("correct_count", 0),
                "Score %": score,
                "Status": status,
                "Details": res.get("details", []),
            })
