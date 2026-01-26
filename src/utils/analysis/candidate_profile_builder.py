from src.utils.analysis.l4_code_analyzer import analyze_l4_code
from src.utils.analysis.round_strength_profiler import profile_round_strengths


def build_candidate_profile(all_results: dict) -> dict:
    profile = {
        "overall_level": "Unknown",
        "strong_areas": [],
        "weak_areas": [],
        "l4_analysis": {},
        "round_insights": {}
    }

    profile["round_insights"] = profile_round_strengths(all_results)

    l4_result = all_results.get("L4")
    if l4_result:
        l4_analysis = analyze_l4_code(l4_result)
        profile["l4_analysis"] = l4_analysis
        profile["overall_level"] = l4_analysis.get("level", "Unknown")

        profile["strong_areas"].extend(l4_analysis.get("strengths", []))
        profile["weak_areas"].extend(l4_analysis.get("weaknesses", []))

    return profile