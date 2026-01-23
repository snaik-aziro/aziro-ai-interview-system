import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib import colors

# ✅ STEP 1: NEW IMPORTS (ONLY THESE)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
from reportlab.lib.units import inch

from src.utils.analysis.summary_generator import (
    generate_round_summary,
    generate_l4_detailed_summary,
    generate_overall_candidate_summary,
)

# =========================================================
# THEME COLORS (ORG SAFE)
# =========================================================
HEADING_COLOR = colors.HexColor("#1F4FD8")
TEXT_COLOR = colors.black
CODE_COLOR = colors.HexColor("#1F4FD8")

PAGE_WIDTH, PAGE_HEIGHT = A4
LEFT_MARGIN = 50
TOP_MARGIN = PAGE_HEIGHT - 50
BOTTOM_MARGIN = 50


def generate_l4_pdf(output_dir: str, uid: str, cand: dict, all_results: dict) -> str:
    """
    Generates a clean, well-formatted PDF report.
    Evaluation logic untouched.
    """

    os.makedirs(output_dir, exist_ok=True)
    pdf_path = os.path.join(output_dir, f"{uid}_role.pdf")

    c = canvas.Canvas(pdf_path, pagesize=A4)
    y = TOP_MARGIN

    # =====================================================
    # Helpers
    # =====================================================
    def new_page():
        nonlocal y
        c.showPage()
        y = TOP_MARGIN

    def ensure_space(lines=1):
        nonlocal y
        if y - (lines * 14) < BOTTOM_MARGIN:
            new_page()

    def write_heading(text):
        nonlocal y
        ensure_space(2)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(HEADING_COLOR)
        c.drawString(LEFT_MARGIN, y, text)
        y -= 20
        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", 10)

    def write_subheading(text):
        nonlocal y
        ensure_space(1)
        c.setFont("Helvetica-Bold", 10)
        c.drawString(LEFT_MARGIN, y, text)
        y -= 16
        c.setFont("Helvetica", 10)

    def write_text(text, indent=20, gap=14):
        nonlocal y
        ensure_space(1)
        c.drawString(LEFT_MARGIN + indent, y, text)
        y -= gap

    def write_code_block(code: str):
        nonlocal y
        ensure_space(3)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(CODE_COLOR)

        for line in code.splitlines():
            if y < BOTTOM_MARGIN:
                new_page()
                c.setFont("Helvetica-Bold", 9)
                c.setFillColor(CODE_COLOR)

            c.drawString(LEFT_MARGIN + 10, y, line)
            y -= 12

        c.setFillColor(TEXT_COLOR)
        c.setFont("Helvetica", 10)

    # =====================================================
    # ✅ STEP 2: NEW PARAGRAPH HELPER (ADDED ONLY)
    # =====================================================
    def write_paragraph(text, indent=20, max_width=PAGE_WIDTH - LEFT_MARGIN * 2):
        nonlocal y

        style = getSampleStyleSheet()["Normal"]
        style.fontName = "Helvetica"
        style.fontSize = 10
        style.leading = 14

        para = Paragraph(text, style)
        w, h = para.wrap(max_width - indent, PAGE_HEIGHT)

        if y - h < BOTTOM_MARGIN:
            new_page()

        para.drawOn(c, LEFT_MARGIN + indent, y - h)
        y -= h + 6

    # =====================================================
    # HEADER
    # =====================================================
    c.setFont("Helvetica-Bold", 11)
    c.drawString(LEFT_MARGIN, y, f"Candidate Name : {cand['name']}")
    y -= 16
    c.drawString(LEFT_MARGIN, y, f"Email          : {cand['email']}")
    y -= 16
    c.drawString(LEFT_MARGIN, y, f"UID            : {uid}")
    y -= 16
    c.drawString(LEFT_MARGIN, y, f"Role           : {cand['role']}")
    y -= 22

    c.line(LEFT_MARGIN, y, PAGE_WIDTH - LEFT_MARGIN, y)
    y -= 20

    # =====================================================
    # NON-L4 ROUNDS (L1, L2, L3, L5, L6)
    # =====================================================
    for rnd in ["L1", "L2", "L3", "L5", "L6"]:
        res = all_results.get(rnd)
        if not res:
            continue

        write_heading(f"{rnd} ROUND")

        write_text(f"Total Questions : {res.get('total_questions', 0)}")
        write_text(f"Score %         : {res.get('score_percent', 0.0)}")
        write_text(f"Status          : {res.get('status', 'NO_RESPONSE')}")

        summary_text = generate_round_summary(rnd, res)
        # ✅ STEP 3 (1): FIXED SUMMARY RENDERING
        write_paragraph(f"<b>Summary :</b> {summary_text}")

        y -= 10

    # =====================================================
    # L4 CODING ROUND
    # =====================================================
    l4 = all_results.get("L4")
    if l4:
        write_heading("L4 CODING ROUND – DETAILED EVALUATION")

        write_text(f"Score  : {l4.get('score_percent', 0.0)}%")
        write_text(f"Status : {l4.get('status')}")

        # Execution details
        details = l4.get("details", [])
        if details:
            y -= 6
            write_subheading("Execution Details")
            for idx, d in enumerate(details, 1):
                write_text(f"{idx}. {d.get('title')}", indent=20)
                write_text(f"Result   : {d.get('user_answer')}", indent=40)
                write_text(f"Expected : {d.get('correct_answer')}", indent=40)
                write_text(f"Correct  : {d.get('is_correct')}", indent=40)
                y -= 6

        # L4 Summary
        l4_summary = generate_l4_detailed_summary(l4)
        write_subheading("Summary")
        # ✅ STEP 3 (2): FIXED L4 SUMMARY
        write_paragraph(l4_summary, indent=20)

        # Submitted code
        submitted_code = l4.get("submitted_code")
        if submitted_code:
            write_subheading("SUBMITTED CODE")
            write_code_block(submitted_code)
        else:
            write_text("No code submission found.", indent=20)

    # =====================================================
    # OVERALL CANDIDATE SUMMARY
    # =====================================================
    write_heading("OVERALL CANDIDATE SUMMARY")
    overall_summary = generate_overall_candidate_summary(all_results)
    # ✅ STEP 3 (3): FIXED OVERALL SUMMARY
    write_paragraph(overall_summary, indent=20)

    # =====================================================
    # FINALIZE
    # =====================================================
    c.save()
    return pdf_path
