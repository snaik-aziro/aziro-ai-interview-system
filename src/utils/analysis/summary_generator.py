def generate_round_summary(round_name: str, result: dict) -> str:
    """
    Generates detailed, HR-readable summary for non-coding rounds.
    Deterministic. Rule-based. Audit-safe.
    """

    score = result.get("score_percent", 0.0)
    correct = result.get("correct_count", 0)
    total = result.get("total_questions", 0)

    if total == 0:
        return f"{round_name}: Not attempted."

    if score >= 85:
        return (
            f"Strong performance in {round_name}. "
            f"Candidate answered {correct} out of {total} questions correctly, "
            f"demonstrating strong conceptual clarity and accuracy."
        )

    if score >= 60:
        return (
            f"Moderate performance in {round_name}. "
            f"Candidate shows acceptable understanding but has gaps in certain areas."
        )

    if score > 0:
        return (
            f"Weak performance in {round_name}. "
            f"Candidate struggled with core concepts and requires improvement."
        )

    return f"{round_name}: Unable to demonstrate required skills."


def generate_l4_detailed_summary(l4_result: dict) -> str:
    """
    Generates deep L4 coding round summary.
    No AI. No speculation.
    """

    score = l4_result.get("score_percent", 0.0)
    details = l4_result.get("details", [])
    code = l4_result.get("submitted_code")

    passed_tests = len([d for d in details if d.get("is_correct")])
    total_tests = len(details)

    summary_parts = []

    if score >= 85:
        summary_parts.append(
            "Candidate demonstrated strong problem-solving skills with a logically sound approach."
        )
    elif score >= 60:
        summary_parts.append(
            "Candidate showed a reasonable approach but missed certain edge cases or optimizations."
        )
    else:
        summary_parts.append(
            "Candidate attempted the problem but was unable to produce a fully correct solution."
        )

    if code:
        summary_parts.append(
            "Code structure indicates familiarity with the programming language and control flow constructs."
        )
    else:
        summary_parts.append(
            "No valid code submission was found."
        )

    if passed_tests < total_tests:
        summary_parts.append(
            "Some test cases failed, indicating gaps in edge-case handling or logic completeness."
        )

    return " ".join(summary_parts)


def generate_overall_candidate_summary(all_results: dict) -> str:
    """
    Consolidated summary across all rounds.
    """

    strengths = []
    weaknesses = []

    for rnd, res in all_results.items():
        score = res.get("score_percent", 0.0)

        if score >= 75:
            strengths.append(rnd)
        elif score > 0:
            weaknesses.append(rnd)

    summary_parts = []

    if strengths:
        summary_parts.append(
            f"Candidate performed well in the following rounds: {', '.join(strengths)}."
        )

    if weaknesses:
        summary_parts.append(
            f"Candidate showed weaker performance in the following rounds: {', '.join(weaknesses)}."
        )

    if not summary_parts:
        summary_parts.append(
            "Insufficient data available to draw a consolidated conclusion."
        )

    return " ".join(summary_parts)