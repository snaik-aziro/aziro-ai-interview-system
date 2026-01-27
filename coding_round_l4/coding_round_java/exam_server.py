from flask import Flask, render_template, request, jsonify
import yaml, subprocess, os, sys, json, time, random

# =====================================================
# SERVER CONFIG
# =====================================================
if len(sys.argv) < 2:
    raise RuntimeError("Usage: python exam_server.py <port>")

PORT = int(sys.argv[1])

UID = os.environ.get("CANDIDATE_UID")
if not UID:
    raise RuntimeError("CANDIDATE_UID is required")

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)

RESULT_FILE = os.path.join(BASE, f"java_result_{UID}.json")
QUESTION_FILE = os.path.join(BASE, f"java_question_{UID}.json")

# =====================================================
# LOAD QUESTIONS
# =====================================================
with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

# =====================================================
# ASSIGN ONE QUESTION PER CANDIDATE (PERSISTED)
# =====================================================
def get_assigned_question():
    if os.path.exists(QUESTION_FILE):
        with open(QUESTION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    question = random.choice(QUESTIONS)

    with open(QUESTION_FILE, "w", encoding="utf-8") as f:
        json.dump(question, f, indent=2)

    return question

# =====================================================
# JAVA STARTER CODE (UNCHANGED)
# =====================================================
JAVA_STARTER = """class Main {

    // Candidate writes ONLY this method
    // input is ALWAYS a STRING
    public static Object solve(String input) {

        return null;
    }

    // ⚠️ DO NOT EDIT
    public static void main(String[] args) {
        if (args.length == 0) return;
        System.out.print(solve(args[0]));
    }
}
"""

# =====================================================
# JAVA EXECUTOR (UNCHANGED)
# =====================================================
def run_java(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_java.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    payload = json.dumps({"code": code, "args": args})
    out, _ = p.communicate(payload)
    return json.loads(out)

# =====================================================
# ROUTES
# =====================================================
@app.route("/")
def index():
    question = get_assigned_question()
    return render_template(
        "index.html",
        question=question,
        starter=JAVA_STARTER
    )

@app.route("/run_code", methods=["POST"])
def run_code():
    data = request.get_json(force=True)

    code = data["code"]
    submit = bool(data.get("submit", False))
    run_hidden = bool(data.get("run_hidden", False))

    question = get_assigned_question()

    public_tests = question["public_tests"]
    hidden_tests = question.get("hidden_tests", [])

    tests = public_tests
    if submit or run_hidden:
        tests = public_tests + hidden_tests

    passed = 0
    results = []

    for idx, t in enumerate(tests):
        res = run_java(code, t["input"])

        if res["returncode"] != 0:
            return jsonify({
                "error": True,
                "message": res["stderr"]
            })

        actual = (res["stdout"] or "").strip()
        expected = str(t["expected"]).strip()

        is_passed = actual == expected
        if is_passed:
            passed += 1

        results.append({
            "index": idx + 1,
            "passed": is_passed,
            "input": t["input"],
            "expected": expected,
            "actual": actual,
            "visibility": "public" if idx < len(public_tests) else "hidden"
        })

    if submit:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "question": question["title"],
                "passed": passed,
                "total": len(tests),
                "results": results,
                "timestamp": time.time()
            }, f, indent=2)

    return jsonify({
        "passed": passed,
        "total": len(tests),
        "test_results": results
    })

# =====================================================
# BOOT
# =====================================================
if __name__ == "__main__":
    print(f"🚀 Java Coding Round → http://localhost:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)
