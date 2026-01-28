from flask import Flask, flash, render_template, redirect, url_for, request, session
import os
import sys
import time
import socket
import subprocess
from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv 
from authlib.integrations.flask_client import OAuth

from dotenv import load_dotenv 

# PATH FIX
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# REAL BACKEND IMPORTS
from generate_candidate_test import run_candidate_test_generation_by_role
from src.utils.google_forms.create_all_forms import create_all_google_forms


app = Flask(__name__)
app.secret_key = "aziro-secret-key"

# -------------------------------------------------
# PATH FIX (reuse project backend)
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

# -------------------------------------------------
# IMPORT REAL BACKEND LOGIC (REUSED)
# -------------------------------------------------
from generate_candidate_test import run_candidate_test_generation_by_role
from src.utils.google_forms.create_all_forms import create_all_google_forms

# ------------------------------------------------- 
# GOOGLE OAUTH CONFIG
# ------------------------------------------------- 
load_dotenv()

oauth = OAuth(app) 
google = oauth.register( 
    name="google", 
    client_id=os.getenv("GOOGLE_CLIENT_ID"), 
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"), 
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration", 
    client_kwargs={"scope": "openid email profile"} )


# -------------------------------------------------
# HELPERS
# -------------------------------------------------
def get_vm_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

ROLE_OPTIONS = {
    "Python Entry Level (0–2 Years)": "python_entry",
    "Java Entry Level (0–2 Years)": "java_entry",
    "JavaScript Entry Level (0–2 Years)": "js_entry",
    "Python QA / System / Linux (4+ Years)": "python_qa_linux",
    "Python QA (4+ Years)": "python_qa",
    "Python Development (4+ Years)": "python_dev",
    "Python + AI/ML (4+ Years)": "python_ai_ml",
    "Java + AWS Development (5+ Years)": "java_aws",
    "Java QA (5+ Years)": "java_qa",
}

# -------------------------------------------------
# ROUND DISPLAY LABELS (UI ONLY)
# -------------------------------------------------
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
    "python_qa_linux": {
        "L1": "Linux",
        "L2": "Python",
        "L3": "QA & Testing",
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
    UI-only helper: returns human-readable round label.
    """
    base = ROUND_LABELS_BY_ROLE.get(role_key, {})

    if round_key == "L4":
        return "Coding Round"

    if domain and domain != "None":
        if round_key == "L5":
            return f"Domain – {domain.capitalize()}"
        if round_key == "L6":
            return "Soft Skills"

    return base.get(round_key, round_key)

# -------------------------------------------------
# ROUTES
# -------------------------------------------------
@app.route("/login", methods=["GET", "POST"]) 
def login(): 
    if request.method == "POST": 
        username = request.form.get("username") 
        password = request.form.get("password") 
        if username and username.endswith("@aziro.com"): 
            session["logged_in"] = True 
            session["username"] = username 
            return redirect(url_for("dashboard")) 
        else: return render_template("login.html", error="Invalid credentials. Please try again.") 
    return render_template("login.html") 

@app.route("/google-login") 
def google_login(): 
    redirect_uri = url_for(
        "google_callback", 
        _external=True)
    print("Redirect URI being used:", redirect_uri) # Debug line
    return google.authorize_redirect(redirect_uri, prompt="login") 

@app.route("/google-callback")
def google_callback():
    try:
        token = google.authorize_access_token()
        user_info = google.get(
            "https://openidconnect.googleapis.com/v1/userinfo"
        ).json()

        print("User info:", user_info)

        email = user_info.get("email")

        if not email or not email.endswith("@aziro.com"):
            flash("Only aziro.com accounts are allowed.")
            return redirect(url_for("login"))

        session["logged_in"] = True
        session["username"] = email

        if session.get("forgot_password_flow"):
            session.pop("forgot_password_flow", None)

        return redirect(url_for("dashboard"))

    except Exception as e:
        print("OAuth error:", e)
        return f"OAuth failed: {e}", 400



@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/create-test", methods=["GET", "POST"])
def create_test():
    if request.method == "POST":

        # -------------------------------
        # 1. Read form inputs
        # -------------------------------
        name = request.form.get("name")
        email = request.form.get("email")
        role_label = request.form.get("role")
        domain = request.form.get("domain")

        role_key = ROLE_OPTIONS.get(role_label)
        domain_selected = domain and domain != "None"

        # -------------------------------
        # 2. Generate candidate JSON
        # -------------------------------
        uid, json_path = run_candidate_test_generation_by_role(
            full_name=name,
            email=email,
            role_key=role_key,
            domain=None if not domain_selected else domain.lower(),
        )

        # -------------------------------
        # 3. Create Google Forms
        # -------------------------------
        raw_forms = create_all_google_forms(json_path)

        forms = {
            "L1": raw_forms.get("L1"),
            "L2": raw_forms.get("L2"),
            "L3": raw_forms.get("L3"),
        }

        if domain_selected:
            forms["L5"] = raw_forms.get("L5")
            forms["L6"] = raw_forms.get("L6")
        else:
            forms["L5"] = raw_forms.get("L5")

        # -------------------------------
        # 4. Start L4 coding server
        # -------------------------------
        port = 5001
        while True:
            try:
                s = socket.socket()
                s.bind(("127.0.0.1", port))
                s.close()
                break
            except OSError:
                port += 1

        subprocess.Popen(
            [sys.executable, os.path.join(PROJECT_ROOT, "coding_round_l4", "exam_server.py"), str(port)],
            cwd=os.path.join(PROJECT_ROOT, "coding_round_l4"),
        )

        time.sleep(1)
        forms["L4"] = f"http://{get_vm_ip()}:{port}"

        # -------------------------------
        # 5. Build UI-friendly test links
        # -------------------------------
        tests = {}

        for rnd, entry in forms.items():
            if not entry:
                continue

            if rnd == "L4":
                url = entry
            else:
                url = entry["responder_url"]

            tests[rnd] = {
                "label": get_round_label(
                    role_key,
                    rnd,
                    None if not domain_selected else domain
                ),
                "url": url,
            }

        # -------------------------------
        # 6. Store in session
        # -------------------------------
        generated_tests = session.get("generated_tests", [])
        generated_tests.append({
            "uid": uid,
            "json_path": json_path,
            "name": name,
            "email": email,
            "role": role_label,
            "domain": domain,
            "tests": tests,
        })

        session["generated_tests"] = generated_tests

        return redirect(url_for("generated_tests"))

    return render_template("test_create.html")


@app.route("/generated-tests")
def generated_tests():
    return render_template(
        "generated_tests.html",
        candidates=session.get("generated_tests", [])
    )


@app.route("/evaluation")
def evaluation():
    return render_template("evaluation.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route('/forgot-password-google')
def forgot_password_google(): 
    return redirect(url_for('google_login'))


# -------------------------------------------------
# ENTRY POINT
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
