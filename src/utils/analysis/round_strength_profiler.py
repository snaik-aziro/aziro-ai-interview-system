def profile_round_strengths(all_results: dict) -> dict:
    """
    Converts round scores into deterministic insights.
    No AI.
    No assumptions.
    """

    insights = {}

    for rnd, res in all_results.items():
        score = res.get("score_percent", 0.0)

        if rnd == "L1":
            insights[rnd] = (
                "Strong logical reasoning"
                if score >= 70 else
                "Logical reasoning needs improvement"
            )

        elif rnd == "L2":
            insights[rnd] = (
                "Strong Python fundamentals"
                if score >= 75 else
                "Python fundamentals need strengthening"
            )

        elif rnd == "L3":
            insights[rnd] = (
                "Good debugging skills"
                if score >= 70 else
                "Debugging and fault isolation are weak"
            )

        elif rnd == "L5":
            insights[rnd] = (
                "Acceptable communication and soft skills"
                if score >= 60 else
                "Soft skills require improvement"
            )

    return insights