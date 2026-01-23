import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))


def generate_hr_summary(profile: dict) -> str:
    """
    Gemini is used ONLY to rewrite structured data into HR-friendly language.
    Safe mode:
    - If Gemini fails (quota, expiry, network, API error)
    - Function returns None
    - System automatically falls back to Python summary
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
Generate a professional HR-facing candidate evaluation summary.
Do not exaggerate.
Do not speculate.
Base everything strictly on the provided data.

Candidate Profile:
{profile}

Limit output to 120 words.
"""

        response = model.generate_content(prompt)
        return response.text.strip()

    except Exception:
        # Gemini failure → silent fallback
        return None
