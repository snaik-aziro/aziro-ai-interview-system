from flask import Flask, render_template, request, jsonify
import yaml, subprocess, os, random, sys, json
from datetime import datetime
import time
import ast


# =====================================================
# EXAM TIMER CONFIG
# =====================================================
EXAM_DURATION_SECONDS = 6 * 60 * 60  # 6 hours
SERVER_START_TIME = time.time()

# =====================================================
# SERVER CONTEXT (PORT + UID) — FINAL & STABLE
# =====================================================

# PORT: only from CLI
if len(sys.argv) < 2:
    raise RuntimeError(
        "Port missing. Run as: python exam_server.py <port>"
    )

PORT = int(sys.argv[1])

# UID: only from ENV (no argv, no fallback)
UID = os.environ.get("CANDIDATE_UID")
if not UID:
    raise RuntimeError(
        "CANDIDATE_UID is mandatory.\n"
        "Example:\n"
        "CANDIDATE_UID=test_user python exam_server.py 5001"
    )

BASE = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE)

app = Flask(__name__)

# =====================================================
# PER-CANDIDATE RESULT FILE
# =====================================================
RESULT_FILE = os.path.join(BASE, f"l4_result_{UID}.json")



with open("questions.yaml", "r", encoding="utf-8") as f:
    QUESTIONS = yaml.safe_load(f)

ASSIGNED_QUESTION = random.choice(QUESTIONS)

def is_exam_expired():
    return (time.time() - SERVER_START_TIME) > EXAM_DURATION_SECONDS

# ---------------- PARAM INFERENCE ----------------
def infer_params(sample_input):
    names = []
    for i, v in enumerate(sample_input):
        if isinstance(v, list):
            names.append(f"arr{i}")
        elif isinstance(v, str):
            names.append(f"s{i}")
        else:
            names.append(f"x{i}")
    return names

def normalize(value):
    if isinstance(value, str):
        v = value.strip()

        if v.lower() == "true":
            return True
        if v.lower() == "false":
            return False

        # numeric string
        if v.isdigit():
            return int(v)

        return v

    if isinstance(value, float):
        return round(value, 6)

    if isinstance(value, list):
        return [normalize(v) for v in value]

    if isinstance(value, dict):
        return {str(k): normalize(v) for k, v in sorted(value.items())}

    return value



# ---------------- STARTER CODE ----------------
def generate_starter_code(question, lang):
    sample_input = question["public_tests"][0]["input"]
    params = infer_params(sample_input)
    args = ", ".join(params)

    if lang == "python":
        return f"""def solve({args}):
    pass
"""
    elif lang == "javascript":
        return """function solve(input) {
    /*
    IMPORTANT:
    ----------
    The platform already passes the correct value to this function.

    Examples:
    Input in question: [[1,2,3]]
    You receive here: [1,2,3]

    Input in question: ["abc"]
    You receive here: "abc"

    Input in question: [10, 20]
    You receive here: 10, 20 (as separate parameters ONLY if question defines so)

    👉 DO NOT do input[0] unless the problem explicitly needs it.
    */

    // write your logic here

    // MUST return the final output
}
"""


    elif lang == "java":
        return """class Main {

    // Candidate writes ONLY this method
    // Input is ALWAYS a STRING
    // Examples:
    // "123", "[123]", "abc", "()[]{}"
    // You MUST return the final answer
    public static Object solve(Object input) {

        String s = input.toString().trim();

        // write your logic using string s
        return null;
    }

    // ⚠️ DO NOT MODIFY main()
    public static void main(String[] args) {
        if (args.length == 0) {
            System.out.print("");
            return;
        }

        Object result = solve(args[0]);
        if (result != null) {
            System.out.print(result.toString());
        }
    }
}
"""



    elif lang == "c":
        return """#include <stdio.h>

/*
 * INPUT FORMAT:
 * - Input is already provided by the platform
 * - Example input: [1,2,3]
 *
 * TASK:
 * - Write logic inside solve()
 * - PRINT the final answer using printf()
 */

void solve(int arr[], int n) {
    // write your logic here
    // example:
    // printf("%d", result);
}

int main() {
    int arr[1000];
    int n = 0;

    // platform feeds input, you DON'T worry about it
    while (scanf("%d", &arr[n]) == 1) {
        n++;
        if (getchar() != ',') break;
    }

    solve(arr, n);
    return 0;
}
"""

    elif lang == "cpp":
        return """#include <bits/stdc++.h>
using namespace std;

/*
 * INPUT FORMAT:
 * - Input is already provided by the platform
 * - Example input: [1,2,3]
 *
 * TASK:
 * - Write logic inside solve()
 * - PRINT the final answer using cout
 */

void solve(vector<int>& arr) {
    // write your logic here
    // example:
    // cout << result;
}

int main() {
    vector<int> arr;
    int x;
    char ch;

    while (cin >> x) {
        arr.push_back(x);
        if (!(cin >> ch)) break;
    }

    solve(arr);
    return 0;
}
"""

    return ""


# ---------------- EXECUTORS ----------------
def run_python(code, args):
    p = subprocess.Popen(
        ["python3", "executors/run_python.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_js(code, args):
    p = subprocess.Popen(
        ["node", "executors/run_js.js"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_java(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_java.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)


def run_c(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_c.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)

def run_cpp(code, args):
    p = subprocess.Popen(
        ["bash", "executors/run_cpp.sh"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    out, _ = p.communicate(json.dumps({"code": code, "args": args}))
    return json.loads(out)


LANG_EXEC = {
    "python": run_python,
    "javascript": run_js
}


# ---------------- ROUTES ----------------
@app.route("/")
def index():
    if is_exam_expired():
        return (
            "<h3>⏰ This coding test has expired.</h3>"
            "<p>Please contact HR for further instructions.</p>",
            403
        )

    return render_template(
    "index.html",
    question=ASSIGNED_QUESTION,
    starters={
        "python": generate_starter_code(ASSIGNED_QUESTION, "python"),
        "javascript": generate_starter_code(ASSIGNED_QUESTION, "javascript"),
        "java": generate_starter_code(ASSIGNED_QUESTION, "java"),
        "c": generate_starter_code(ASSIGNED_QUESTION, "c"),
        "cpp": generate_starter_code(ASSIGNED_QUESTION, "cpp"),
    }
)

@app.route("/run_code", methods=["POST"])
def run_code():
    if is_exam_expired():
        return jsonify({
            "error": True,
            "message": "⏰ This coding test has expired. Submission is disabled."
        }), 403

    data = request.get_json(force=True)

    code = data["code"]
    lang = data["language"]
    submit = bool(data.get("submit", False))
    run_hidden = bool(data.get("run_hidden", False))
    focus_lost = int(data.get("focus_lost", 0))

    public_tests = ASSIGNED_QUESTION["public_tests"]
    hidden_tests = ASSIGNED_QUESTION["hidden_tests"]

    tests = public_tests
    if run_hidden or submit:
        tests = public_tests + hidden_tests

    executor = LANG_EXEC[lang]
    passed = 0
    test_results = []

    for idx, t in enumerate(tests):
        res = executor(code, t["input"])

        if res.get("returncode", 0) != 0:
            return jsonify({
                "error": True,
                "message": res.get("stderr", "Execution error")
            })

        stdout = res.get("stdout") or ""
        stdout = stdout.strip()
        expected_value = t.get("expected")

        # -------------------------------
        # 🔥 LANGUAGE-SAFE RESULT PARSING
        # -------------------------------

        if lang in ("c", "cpp"):
            # C / C++ → candidate PRINTS output
            actual_value = stdout
            expected_norm = str(expected_value).strip()
            is_passed = actual_value == expected_norm

        else:
            # Python / JS / Java
            try:
                actual_value = ast.literal_eval(stdout)
            except:
                actual_value = stdout

            is_passed = normalize(actual_value) == normalize(expected_value)

        if is_passed:
            passed += 1

        visibility = "public" if idx < len(public_tests) else "hidden"

        test_results.append({
            "index": idx + 1,
            "passed": is_passed,
            "input": t["input"],
            "expected": expected_value,
            "actual": actual_value,
            "visibility": visibility
        })

    total = len(tests)
    score = round((passed / total) * 100, 2) if total else 0.0
    status = "PASS" if score >= 65 else "FAIL"

    if submit:
        with open(RESULT_FILE, "w", encoding="utf-8") as f:
            json.dump({
                "passed": passed,
                "total": total,
                "score_percent": score,
                "language": lang,
                "focus_lost": focus_lost,
                "status": status,
                "timestamp": datetime.utcnow().isoformat(),
                "submitted_code": code,
                "test_cases": test_results
            }, f, indent=2)

    return jsonify({
        "passed": passed,
        "total": total,
        "score_percent": score,
        "status": status,
        "test_results": test_results,
        "focus_warnings": focus_lost
    })


if __name__ == "__main__":
    vm_ip = os.environ.get("VM_IP", "localhost")
    print(f"🚀 L4 server running at http://{vm_ip}:{PORT}")
    app.run(host="0.0.0.0", port=PORT, debug=False)