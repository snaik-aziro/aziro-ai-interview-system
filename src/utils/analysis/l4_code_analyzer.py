import ast
from typing import Dict


def analyze_l4_code(l4_result: dict) -> dict:
    """
    Deterministic, rule-based L4 code analysis.
    Does NOT change scoring.
    Does NOT use AI.
    """

    submitted_code = l4_result.get("submitted_code", "")
    details = l4_result.get("details", [])
    score = l4_result.get("score_percent", 0.0)

    analysis = {
        "approach": "unknown",
        "complexity": "unknown",
        "language_fluency": "basic",
        "code_style": "unknown",
        "edge_case_handling": "unknown",
        "strengths": [],
        "weaknesses": [],
        "level": "Beginner"
    }

    if not submitted_code:
        analysis["weaknesses"].append("No code submission")
        return analysis

    # -----------------------------
    # Safe AST parsing
    # -----------------------------
    try:
        tree = ast.parse(submitted_code)
    except SyntaxError:
        analysis["weaknesses"].append("Syntax errors in submitted code")
        return analysis

    loops = sum(isinstance(n, (ast.For, ast.While)) for n in ast.walk(tree))
    conditionals = sum(isinstance(n, ast.If) for n in ast.walk(tree))

    if loops >= 1 and conditionals >= 1:
        analysis["approach"] = "iterative logic with conditions"

    code_lower = submitted_code.lower()

    if any(fn in code_lower for fn in ["isalpha", "isdigit", "split", "join"]):
        analysis["language_fluency"] = "intermediate"
        analysis["strengths"].append("Good use of Python built-in methods")

    if loops == 1:
        analysis["complexity"] = "O(n)"
    elif loops > 1:
        analysis["complexity"] = "O(n²)"

    if len(submitted_code.splitlines()) >= 6:
        analysis["code_style"] = "structured"
        analysis["strengths"].append("Readable and structured code")

    failed_tests = [d for d in details if not d.get("is_correct")]
    if failed_tests:
        analysis["edge_case_handling"] = "partial"
        analysis["weaknesses"].append("Edge cases not fully handled")
    else:
        analysis["edge_case_handling"] = "good"

    if score >= 85:
        analysis["level"] = "Advanced"
    elif score >= 60:
        analysis["level"] = "Intermediate"
    else:
        analysis["level"] = "Beginner"

    return analysis