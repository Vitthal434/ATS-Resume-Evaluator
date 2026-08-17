"""
ResumeIQ — Stage 9.6 / Final Visual Polish PDF Report Generator

Generates a production-quality, multi-page, typeset PDF report using ReportLab.
Features:
  - Modern ResumeIQ branding header/footer with dynamic page numbers
  - Executive Score Hero with 4-card metric layout (Overall, Skill 50%, Text 30%, Experience 20%)
  - Clean methodology transparent callout note
  - Visual Skill Intelligence: 2-3 column styled badge/chip grids for Matched, Missing, and Partial skills
  - Gap Analysis Coverage metric strip
  - Prioritized Improvement Roadmap with HIGH / MEDIUM / LOW color-coded tiers
  - Deterministic Career Alignment (Recommended Job Roles) table
  - Optional AI-Assisted Guidance callout card (supplementary only)
  - Smart KeepTogether guards to eliminate orphan headings and awkward blank pages
"""

import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.platypus.flowables import HRFlowable

# ---------------------------------------------------------------------------
# Constants & Palette (ResumeIQ Modern Design System)
# ---------------------------------------------------------------------------
BRAND_NAME = "ResumeIQ"
REPORT_SUBTITLE = "Professional ATS Resume Analysis Report"
REPORT_FILE_PATH = os.path.join("reports", "ATS_Report.pdf")

# Palette
PRIMARY_BLUE = colors.HexColor("#2563eb")     # Brand primary
PRIMARY_DARK = colors.HexColor("#1e40af")     # Navy dark
PRIMARY_NAVY = colors.HexColor("#0f172a")     # Deep slate
PRIMARY_LIGHT = colors.HexColor("#eff6ff")    # Light blue background

TEXT_DARK = colors.HexColor("#0f172a")        # Slate 900
TEXT_BODY = colors.HexColor("#334155")        # Slate 700
TEXT_MUTED = colors.HexColor("#64748b")       # Slate 500

BORDER_LIGHT = colors.HexColor("#e2e8f0")     # Slate 200
BORDER_DARK = colors.HexColor("#cbd5e1")      # Slate 300
SURFACE_WHITE = colors.HexColor("#ffffff")
SURFACE_BG = colors.HexColor("#f8fafc")        # Slate 50
SURFACE_ALT = colors.HexColor("#f1f5f9")       # Slate 100

# Status Accents
ACCENT_SUCCESS = colors.HexColor("#16a34a")   # Green 600
SUCCESS_BG = colors.HexColor("#f0fdf4")       # Green 50
SUCCESS_BORDER = colors.HexColor("#bbf7d0")   # Green 200

ACCENT_WARNING = colors.HexColor("#d97706")   # Amber 600
WARNING_BG = colors.HexColor("#fffbeb")       # Amber 50
WARNING_BORDER = colors.HexColor("#fde68a")   # Amber 200

ACCENT_DANGER = colors.HexColor("#dc2626")    # Red 600
DANGER_BG = colors.HexColor("#fef2f2")        # Red 50
DANGER_BORDER = colors.HexColor("#fecaca")    # Red 200

ACCENT_AI = colors.HexColor("#7c3aed")        # Violet 600
AI_BG = colors.HexColor("#f5f3ff")            # Violet 50
AI_BORDER = colors.HexColor("#ddd6fe")        # Violet 200

# Page Dimensions (Letter: 612 x 792 pt)
PAGE_W, PAGE_H = letter
LEFT_MARGIN = RIGHT_MARGIN = 0.55 * inch      # 39.6 pt
TOP_MARGIN = BOTTOM_MARGIN = 0.55 * inch
CONTENT_WIDTH = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN  # 532.8 pt


# ---------------------------------------------------------------------------
# Skill Display Formatter
# ---------------------------------------------------------------------------
SKILL_MAP = {
    "aws": "AWS",
    "gcp": "GCP",
    "azure": "Azure",
    "api": "API",
    "apis": "APIs",
    "rest api": "REST API",
    "restful api": "RESTful API",
    "rest": "REST",
    "graphql": "GraphQL",
    "html": "HTML",
    "html5": "HTML5",
    "css": "CSS",
    "css3": "CSS3",
    "sql": "SQL",
    "mysql": "MySQL",
    "postgresql": "PostgreSQL",
    "postgres": "PostgreSQL",
    "nosql": "NoSQL",
    "mongodb": "MongoDB",
    "github": "GitHub",
    "git": "Git",
    "oop": "OOP",
    "dsa": "DSA",
    "nlp": "NLP",
    "natural language processing": "Natural Language Processing",
    "ai": "AI",
    "ml": "ML",
    "c++": "C++",
    "c#": "C#",
    ".net": ".NET",
    "power bi": "Power BI",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "react": "React",
    "react.js": "React.js",
    "reactjs": "React.js",
    "vue": "Vue",
    "vue.js": "Vue.js",
    "node": "Node.js",
    "node.js": "Node.js",
    "nodejs": "Node.js",
    "next.js": "Next.js",
    "ci cd": "CI/CD",
    "ci/cd": "CI/CD",
    "devops": "DevOps",
    "kubernetes": "Kubernetes",
    "k8s": "Kubernetes",
    "docker": "Docker",
    "redis": "Redis",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "spring": "Spring Boot",
    "spring boot": "Spring Boot",
    "linux": "Linux",
    "bash": "Bash",
}


def format_skill(skill):
    """Return a display-formatted version of a canonical skill name."""
    if not skill:
        return ""
    skill_str = str(skill).strip()
    if not skill_str:
        return ""
    if " or " in skill_str:
        return " or ".join(format_skill(part) for part in skill_str.split(" or "))
    return SKILL_MAP.get(skill_str.lower(), skill_str.title())


# ---------------------------------------------------------------------------
# Page Canvas Callbacks (Header / Footer)
# ---------------------------------------------------------------------------
def _draw_header_footer(canvas, doc):
    """Draw branding header bar and page-number footer on every page."""
    canvas.saveState()
    page_num = doc.page

    # --- Header Bar (Navy with Blue Accent) ---
    canvas.setFillColor(PRIMARY_DARK)
    canvas.rect(0, PAGE_H - 32, PAGE_W, 32, fill=1, stroke=0)

    canvas.setFillColor(PRIMARY_BLUE)
    canvas.rect(0, PAGE_H - 34, PAGE_W, 2, fill=1, stroke=0)

    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(colors.white)
    canvas.drawString(LEFT_MARGIN, PAGE_H - 21, BRAND_NAME)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#93c5fd"))
    canvas.drawString(LEFT_MARGIN + 68, PAGE_H - 21, "|  Intelligent ATS Evaluation")

    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(colors.HexColor("#cbd5e1"))
    canvas.drawRightString(PAGE_W - RIGHT_MARGIN, PAGE_H - 21, REPORT_SUBTITLE)

    # --- Footer Divider & Metadata ---
    canvas.setStrokeColor(BORDER_LIGHT)
    canvas.setLineWidth(0.75)
    canvas.line(LEFT_MARGIN, 34, PAGE_W - RIGHT_MARGIN, 34)

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(TEXT_MUTED)
    canvas.drawString(
        LEFT_MARGIN,
        22,
        f"{BRAND_NAME} Evaluation Report  ·  Deterministic ATS Engine  ·  {datetime.now().strftime('%d %b %Y')}",
    )
    canvas.drawRightString(PAGE_W - RIGHT_MARGIN, 22, f"Page {page_num}")

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Style Factory
# ---------------------------------------------------------------------------
def _build_styles():
    """Return a dictionary of named ParagraphStyles."""
    styles = {}

    styles["report_title"] = ParagraphStyle(
        "report_title",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=PRIMARY_DARK,
        leading=22,
        spaceAfter=2,
    )
    styles["report_subtitle"] = ParagraphStyle(
        "report_subtitle",
        fontName="Helvetica",
        fontSize=9,
        textColor=TEXT_MUTED,
        leading=12,
        spaceAfter=8,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=PRIMARY_DARK,
        leading=14,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True,
    )
    styles["section_subheading"] = ParagraphStyle(
        "section_subheading",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=TEXT_DARK,
        leading=12,
        spaceBefore=4,
        spaceAfter=3,
        keepWithNext=True,
    )
    styles["normal"] = ParagraphStyle(
        "normal",
        fontName="Helvetica",
        fontSize=9,
        textColor=TEXT_BODY,
        leading=13,
        spaceAfter=2,
    )
    styles["muted"] = ParagraphStyle(
        "muted",
        fontName="Helvetica",
        fontSize=8,
        textColor=TEXT_MUTED,
        leading=11,
        spaceAfter=2,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=TEXT_BODY,
        leading=12,
        leftIndent=8,
        spaceAfter=3,
    )
    styles["ai_body"] = ParagraphStyle(
        "ai_body",
        fontName="Helvetica",
        fontSize=8.5,
        textColor=TEXT_BODY,
        leading=12,
        leftIndent=8,
        spaceAfter=3,
    )
    styles["table_header"] = ParagraphStyle(
        "table_header",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        textColor=colors.white,
        leading=11,
        alignment=TA_LEFT,
    )
    styles["table_cell"] = ParagraphStyle(
        "table_cell",
        fontName="Helvetica",
        fontSize=8,
        textColor=TEXT_BODY,
        leading=11,
    )
    styles["table_cell_bold"] = ParagraphStyle(
        "table_cell_bold",
        fontName="Helvetica-Bold",
        fontSize=8,
        textColor=TEXT_DARK,
        leading=11,
    )
    return styles


# ---------------------------------------------------------------------------
# Visual Component Builders
# ---------------------------------------------------------------------------
def _score_summary_card(score, category, skill_score, text_similarity, experience_score, styles):
    """
    Render an executive 4-card metric strip:
    - Overall ATS Score (Primary Blue Hero Card)
    - Skill Match (50% Weight)
    - Text Relevance (30% Weight)
    - Experience Match (20% Weight)
    """
    card_w1 = CONTENT_WIDTH * 0.31
    card_w2 = CONTENT_WIDTH * 0.23
    card_w3 = CONTENT_WIDTH * 0.23
    card_w4 = CONTENT_WIDTH * 0.23

    # Card 1: Overall ATS Score
    p_overall = Paragraph(
        f"<font size=7 color='#bfdbfe'><b>OVERALL ATS SCORE</b></font><br/>"
        f"<font size=20 color='#ffffff'><b>{score:.1f}%</b></font><br/>"
        f"<font size=8 color='#ffffff'><b>{category}</b></font><br/>"
        f"<font size=6.5 color='#93c5fd'>Weighted ATS Fit</font>",
        ParagraphStyle("hero_card", fontName="Helvetica", leading=13, alignment=TA_CENTER),
    )

    # Card 2: Skill Match
    p_skill = Paragraph(
        f"<font size=7 color='#64748b'><b>SKILL MATCH</b></font><br/>"
        f"<font size=14 color='#1d4ed8'><b>{skill_score:.1f}%</b></font><br/>"
        f"<font size=7.5 color='#0f172a'><b>50% Weight</b></font><br/>"
        f"<font size=6.5 color='#64748b'>Core & related skills</font>",
        ParagraphStyle("card_skill", fontName="Helvetica", leading=12, alignment=TA_CENTER),
    )

    # Card 3: Text Relevance
    p_text = Paragraph(
        f"<font size=7 color='#64748b'><b>TEXT RELEVANCE</b></font><br/>"
        f"<font size=14 color='#1d4ed8'><b>{text_similarity:.1f}%</b></font><br/>"
        f"<font size=7.5 color='#0f172a'><b>30% Weight</b></font><br/>"
        f"<font size=6.5 color='#64748b'>Semantic TF-IDF match</font>",
        ParagraphStyle("card_text", fontName="Helvetica", leading=12, alignment=TA_CENTER),
    )

    # Card 4: Experience Level
    p_exp = Paragraph(
        f"<font size=7 color='#64748b'><b>EXPERIENCE LEVEL</b></font><br/>"
        f"<font size=14 color='#1d4ed8'><b>{experience_score:.1f}%</b></font><br/>"
        f"<font size=7.5 color='#0f172a'><b>20% Weight</b></font><br/>"
        f"<font size=6.5 color='#64748b'>Seniority & tenure fit</font>",
        ParagraphStyle("card_exp", fontName="Helvetica", leading=12, alignment=TA_CENTER),
    )

    data = [[p_overall, p_skill, p_text, p_exp]]
    col_w = [card_w1, card_w2, card_w3, card_w4]

    t = Table(data, colWidths=col_w, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), PRIMARY_BLUE),
        ("BACKGROUND", (1, 0), (-1, 0), SURFACE_BG),
        ("BOX", (0, 0), (0, 0), 1, PRIMARY_DARK),
        ("BOX", (1, 0), (-1, 0), 0.75, BORDER_LIGHT),
        ("INNERGRID", (1, 0), (-1, 0), 0.5, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def _methodology_banner(styles):
    """Render a compact transparent scoring methodology banner."""
    text = (
        "<b>Scoring Transparency:</b> The Overall ATS Score is deterministically computed as: "
        "<b>50% Skill Match</b> + <b>30% Text Relevance</b> + <b>20% Experience Level</b>. "
        "Scoring is 100% objective, rule-verified, and independent of AI provider status."
    )
    p = Paragraph(f"<font size=7.5 color='#334155'>{text}</font>", styles["normal"])
    t = Table([[p]], colWidths=[CONTENT_WIDTH], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE_ALT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def _skills_chip_grid(skills, badge_type="matched"):
    """
    Render skills as a compact 3-column chip grid table.
    badge_type: 'matched' (green), 'missing' (red), 'partial' (amber)
    """
    if not skills:
        return None

    if badge_type == "matched":
        bg_col = SUCCESS_BG
        border_col = SUCCESS_BORDER
        icon = "<font color='#16a34a'><b>✓</b></font>"
        text_col = "#166534"
    elif badge_type == "missing":
        bg_col = DANGER_BG
        border_col = DANGER_BORDER
        icon = "<font color='#dc2626'><b>✗</b></font>"
        text_col = "#991b1b"
    else:
        bg_col = WARNING_BG
        border_col = WARNING_BORDER
        icon = "<font color='#d97706'><b>≈</b></font>"
        text_col = "#92400e"

    cols = 3
    col_width = CONTENT_WIDTH / cols
    rows = []
    current_row = []

    for s in skills:
        formatted = format_skill(s)
        chip_para = Paragraph(
            f"{icon}  <font size=8 color='{text_col}'><b>{formatted}</b></font>",
            ParagraphStyle("chip", fontName="Helvetica", leading=10),
        )
        current_row.append(chip_para)
        if len(current_row) == cols:
            rows.append(current_row)
            current_row = []

    if current_row:
        while len(current_row) < cols:
            current_row.append(Paragraph("", ParagraphStyle("empty")))
        rows.append(current_row)

    t = Table(rows, colWidths=[col_width] * cols, hAlign="LEFT")
    t_style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]

    for r_idx, r_data in enumerate(rows):
        for c_idx, cell in enumerate(r_data):
            if cell.text:  # Non-empty chip
                t_style.append(("BACKGROUND", (c_idx, r_idx), (c_idx, r_idx), bg_col))
                t_style.append(("BOX", (c_idx, r_idx), (c_idx, r_idx), 0.5, border_col))

    t.setStyle(TableStyle(t_style))
    return t


def _partial_skills_table(partial_matches, styles):
    """Two-column table for partial/related skills."""
    if not partial_matches:
        return None

    data = [
        [
            Paragraph("<font size=8 color='#ffffff'><b>Required Skill</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Candidate Skill (Related · 50% Credit)</b></font>", styles["table_header"]),
        ]
    ]

    for p in partial_matches:
        req = format_skill(p.get("required_skill", ""))
        cand = format_skill(p.get("candidate_skill", ""))
        p_req = Paragraph(f"<font size=8 color='#0f172a'><b>{req}</b></font>", styles["normal"])
        p_cand = Paragraph(
            f"<font color='#d97706'><b>≈</b></font>  <font size=8 color='#0f172a'><b>{cand}</b></font> "
            f"<font size=7 color='#64748b'>(satisfies {req} with 50% partial credit)</font>",
            styles["normal"],
        )
        data.append([p_req, p_cand])

    col_w = [CONTENT_WIDTH * 0.35, CONTENT_WIDTH * 0.65]
    t = Table(data, colWidths=col_w, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT_WARNING),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE_WHITE, SURFACE_BG]),
    ]))
    return t


def _gap_coverage_strip(coverage, styles):
    """Render a 5-column metric strip for Gap Analysis Coverage."""
    if not coverage or coverage.get("total_requirements", 0) <= 0:
        return None

    total = coverage.get("total_requirements", 0)
    exact = coverage.get("exact_matches", 0)
    partial = coverage.get("partial_matches", 0)
    missing = coverage.get("missing", 0)
    pct = coverage.get("coverage_percentage", 0.0)

    cell_w = CONTENT_WIDTH / 5.0

    c1 = Paragraph(
        f"<font size=6.5 color='#64748b'><b>TOTAL REQUIRED</b></font><br/>"
        f"<font size=11 color='#0f172a'><b>{total}</b></font>",
        ParagraphStyle("cov_1", fontName="Helvetica", leading=11, alignment=TA_CENTER),
    )
    c2 = Paragraph(
        f"<font size=6.5 color='#16a34a'><b>EXACT MATCHES</b></font><br/>"
        f"<font size=11 color='#16a34a'><b>{exact}</b></font>",
        ParagraphStyle("cov_2", fontName="Helvetica", leading=11, alignment=TA_CENTER),
    )
    c3 = Paragraph(
        f"<font size=6.5 color='#d97706'><b>PARTIAL MATCHES</b></font><br/>"
        f"<font size=11 color='#d97706'><b>{partial}</b></font>",
        ParagraphStyle("cov_3", fontName="Helvetica", leading=11, alignment=TA_CENTER),
    )
    c4 = Paragraph(
        f"<font size=6.5 color='#dc2626'><b>MISSING SKILLS</b></font><br/>"
        f"<font size=11 color='#dc2626'><b>{missing}</b></font>",
        ParagraphStyle("cov_4", fontName="Helvetica", leading=11, alignment=TA_CENTER),
    )
    c5 = Paragraph(
        f"<font size=6.5 color='#1d4ed8'><b>EFFECTIVE COVERAGE</b></font><br/>"
        f"<font size=11 color='#1d4ed8'><b>{pct:.1f}%</b></font>",
        ParagraphStyle("cov_5", fontName="Helvetica", leading=11, alignment=TA_CENTER),
    )

    t = Table([[c1, c2, c3, c4, c5]], colWidths=[cell_w] * 5, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SURFACE_BG),
        ("BOX", (0, 0), (-1, -1), 0.75, BORDER_LIGHT),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


def _roadmap_tier_table(gaps, priority_tier, header_bg, styles):
    """
    Render a roadmap tier table (Immediate, Next, or Optional).
    """
    if not gaps:
        return None

    data = [
        [
            Paragraph("<font size=8 color='#ffffff'><b>Skill</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Status</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Impact</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Actionable Recommendation</b></font>", styles["table_header"]),
        ]
    ]

    for g in gaps:
        skill_txt = format_skill(g.get("skill", ""))
        status_txt = g.get("status", "").upper()
        impact_txt = g.get("estimated_impact", "").upper()
        rec_txt = g.get("recommendation", "")

        # Format status badge
        if status_txt == "MISSING":
            status_html = "<font size=7 color='#dc2626'><b>MISSING</b></font>"
        elif status_txt == "PARTIAL":
            status_html = "<font size=7 color='#d97706'><b>PARTIAL</b></font>"
        else:
            status_html = f"<font size=7 color='#64748b'><b>{status_txt}</b></font>"

        # Format impact badge
        if impact_txt == "HIGH":
            impact_html = "<font size=7 color='#dc2626'><b>HIGH</b></font>"
        elif impact_txt == "MEDIUM":
            impact_html = "<font size=7 color='#d97706'><b>MEDIUM</b></font>"
        else:
            impact_html = "<font size=7 color='#64748b'><b>LOW</b></font>"

        p_skill = Paragraph(f"<font size=8 color='#0f172a'><b>{skill_txt}</b></font>", styles["normal"])
        p_status = Paragraph(status_html, styles["normal"])
        p_impact = Paragraph(impact_html, styles["normal"])
        p_rec = Paragraph(f"<font size=7.5 color='#334155'>{rec_txt}</font>", styles["normal"])

        data.append([p_skill, p_status, p_impact, p_rec])

    col_w = [1.25 * inch, 0.75 * inch, 0.7 * inch, CONTENT_WIDTH - 2.7 * inch]
    t = Table(data, colWidths=col_w, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE_WHITE, SURFACE_BG]),
    ]))
    return t


def _jobs_recommendation_table(recommended_jobs, styles):
    """
    Render recommended career roles table.
    Deterministic alignment from matched resume skills.
    """
    if not recommended_jobs:
        return None

    data = [
        [
            Paragraph("<font size=8 color='#ffffff'><b>Career Role</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Skill Alignment Match</b></font>", styles["table_header"]),
            Paragraph("<font size=8 color='#ffffff'><b>Alignment Status</b></font>", styles["table_header"]),
        ]
    ]

    for job in recommended_jobs:
        title = job.get("job", "")
        score_val = job.get("score", 0)
        if score_val >= 80:
            fit_label = "<font size=7.5 color='#16a34a'><b>Strong Match</b></font>"
            score_color = "#16a34a"
        elif score_val >= 60:
            fit_label = "<font size=7.5 color='#2563eb'><b>Moderate Match</b></font>"
            score_color = "#2563eb"
        else:
            fit_label = "<font size=7.5 color='#64748b'><b>Potential Fit</b></font>"
            score_color = "#64748b"

        p_title = Paragraph(f"<font size=8.5 color='#0f172a'><b>{title}</b></font>", styles["normal"])
        p_score = Paragraph(f"<font size=8.5 color='{score_color}'><b>{score_val}%</b></font>", styles["normal"])
        p_fit = Paragraph(fit_label, styles["normal"])

        data.append([p_title, p_score, p_fit])

    col_w = [CONTENT_WIDTH * 0.52, CONTENT_WIDTH * 0.24, CONTENT_WIDTH * 0.24]
    t = Table(data, colWidths=col_w, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_DARK),
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [SURFACE_WHITE, SURFACE_BG]),
    ]))
    return t


def _section_header(title, styles, subtitle=None):
    """Return section header elements with KeepTogether guard."""
    elements = [
        Spacer(1, 4),
        HRFlowable(width=CONTENT_WIDTH, thickness=0.75, color=BORDER_LIGHT, spaceAfter=3),
        Paragraph(title, styles["section_heading"]),
    ]
    if subtitle:
        elements.append(Paragraph(subtitle, styles["muted"]))
    elements.append(Spacer(1, 3))
    return elements


# ---------------------------------------------------------------------------
# Main PDF Generator Entry Point
# ---------------------------------------------------------------------------
def generate_report(
    score,
    category,
    skill_score,
    text_similarity,
    experience_score,
    matched,
    missing,
    suggestions,
    recommended_jobs,
    gap_analysis=None,
):
    """
    Generate the ATS analysis PDF and return its file path.

    gap_analysis: optional dict from analyze_resume_job_gap() containing
      partial_matches, prioritized_gaps, roadmap, and recommendations.
    """
    os.makedirs("reports", exist_ok=True)

    styles = _build_styles()

    pdf = SimpleDocTemplate(
        REPORT_FILE_PATH,
        pagesize=letter,
        rightMargin=RIGHT_MARGIN,
        leftMargin=LEFT_MARGIN,
        topMargin=TOP_MARGIN + 28,     # Clearance for header bar
        bottomMargin=BOTTOM_MARGIN + 24,  # Clearance for footer bar
        title=f"{BRAND_NAME} — ATS Analysis Report",
        author=BRAND_NAME,
        subject="ATS Resume Evaluation Report",
    )

    story = []

    # -----------------------------------------------------------------------
    # 1. Report Header / Executive Title
    # -----------------------------------------------------------------------
    story.append(Paragraph(BRAND_NAME, styles["report_title"]))
    story.append(Paragraph(REPORT_SUBTITLE, styles["report_subtitle"]))
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 2. Executive Score Summary & Transparent Methodology
    # -----------------------------------------------------------------------
    score_card = _score_summary_card(
        score=score,
        category=category,
        skill_score=skill_score,
        text_similarity=text_similarity,
        experience_score=experience_score,
        styles=styles,
    )
    method_banner = _methodology_banner(styles)

    story.append(KeepTogether([score_card, Spacer(1, 4), method_banner]))
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 3. Gap Analysis Coverage Metric Strip (if available)
    # -----------------------------------------------------------------------
    coverage = (gap_analysis or {}).get("skill_coverage")
    if coverage and coverage.get("total_requirements", 0) > 0:
        cov_strip = _gap_coverage_strip(coverage, styles)
        if cov_strip:
            hdr = _section_header("Gap Analysis & Skill Coverage", styles, "Overall requirement fulfillment breakdown")
            story.append(KeepTogether([*hdr, cov_strip]))
            story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 4. Matched Skills (Visual Badge Grid)
    # -----------------------------------------------------------------------
    matched_skills = [format_skill(s) for s in (matched or [])]
    hdr_matched = _section_header(
        f"Matched Skills ({len(matched_skills)})",
        styles,
        "Skills verified in your resume matching the target job requirements",
    )
    grid_matched = _skills_chip_grid(matched_skills, badge_type="matched")
    if grid_matched:
        story.append(KeepTogether([*hdr_matched, grid_matched]))
    else:
        story.append(KeepTogether([*hdr_matched, Paragraph("No direct skill matches identified.", styles["muted"])]))
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 5. Missing Skills (Visual Badge Grid)
    # -----------------------------------------------------------------------
    missing_skills = [format_skill(s) for s in (missing or [])]
    hdr_missing = _section_header(
        f"Missing Skills & Target Requirements ({len(missing_skills)})",
        styles,
        "Key skills required by the job description that were not detected",
    )
    grid_missing = _skills_chip_grid(missing_skills, badge_type="missing")
    if grid_missing:
        story.append(KeepTogether([*hdr_missing, grid_missing]))
    else:
        story.append(KeepTogether([*hdr_missing, Paragraph("No critical missing skills detected.", styles["muted"])]))
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 6. Partial / Transferable Skills (if present)
    # -----------------------------------------------------------------------
    partial_matches = (gap_analysis or {}).get("partial_matches", [])
    if partial_matches:
        hdr_partial = _section_header(
            f"Transferable & Related Skills ({len(partial_matches)})",
            styles,
            "Candidate skills that partially satisfy requirements (awarded 50% partial credit)",
        )
        tbl_partial = _partial_skills_table(partial_matches, styles)
        if tbl_partial:
            story.append(KeepTogether([*hdr_partial, tbl_partial]))
            story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 7. Suggestions (General Resume Action Items)
    # -----------------------------------------------------------------------
    if suggestions:
        hdr_sug = _section_header(
            "Resume Improvement Action Items",
            styles,
            "High-priority recommendations to enhance ATS keyword positioning",
        )
        sug_items = []
        for sug in suggestions:
            sug_items.append(
                Paragraph(
                    f"<font color='#2563eb'><b>•</b></font>  <font size=8 color='#0f172a'>{sug}</font>",
                    styles["bullet"],
                )
            )
        story.append(KeepTogether([*hdr_sug, *sug_items[:2]]))
        for extra_sug in sug_items[2:]:
            story.append(extra_sug)
        story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 8. Prioritized Improvement Roadmap
    # -----------------------------------------------------------------------
    roadmap = (gap_analysis or {}).get("roadmap", {})
    immediate = roadmap.get("immediate", [])
    next_gaps = roadmap.get("next", [])
    optional_gaps = roadmap.get("optional", [])

    if immediate or next_gaps or optional_gaps:
        hdr_roadmap = _section_header(
            "Prioritized Improvement Roadmap",
            styles,
            "Actionable steps categorized by hiring impact and urgency",
        )
        story.append(KeepTogether(hdr_roadmap))

        if immediate:
            p_imm_hdr = Paragraph(
                "<font size=8.5 color='#dc2626'><b>Immediate Priorities</b></font> "
                "<font size=7.5 color='#64748b'>— High impact gaps to address first</font>",
                styles["section_subheading"],
            )
            tbl_imm = _roadmap_tier_table(immediate, "HIGH", ACCENT_DANGER, styles)
            if tbl_imm:
                story.append(KeepTogether([p_imm_hdr, Spacer(1, 2), tbl_imm]))
                story.append(Spacer(1, 4))

        if next_gaps:
            p_next_hdr = Paragraph(
                "<font size=8.5 color='#d97706'><b>Next Priorities</b></font> "
                "<font size=7.5 color='#64748b'>— Medium impact requirements</font>",
                styles["section_subheading"],
            )
            tbl_next = _roadmap_tier_table(next_gaps, "MEDIUM", ACCENT_WARNING, styles)
            if tbl_next:
                story.append(KeepTogether([p_next_hdr, Spacer(1, 2), tbl_next]))
                story.append(Spacer(1, 4))

        if optional_gaps:
            p_opt_hdr = Paragraph(
                "<font size=8.5 color='#475569'><b>Optional Enhancements</b></font> "
                "<font size=7.5 color='#64748b'>— Secondary / nice-to-have skills</font>",
                styles["section_subheading"],
            )
            tbl_opt = _roadmap_tier_table(optional_gaps, "LOW", colors.HexColor("#475569"), styles)
            if tbl_opt:
                story.append(KeepTogether([p_opt_hdr, Spacer(1, 2), tbl_opt]))
                story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 9. Career Alignment & Recommended Roles (Deterministic)
    # -----------------------------------------------------------------------
    tbl_jobs = _jobs_recommendation_table(recommended_jobs, styles)
    hdr_jobs = _section_header(
        "Career Alignment & Recommended Job Roles",
        styles,
        "Deterministic role recommendations matched against your resume skills",
    )
    if tbl_jobs:
        story.append(KeepTogether([*hdr_jobs, tbl_jobs]))
    else:
        story.append(
            KeepTogether([*hdr_jobs, Paragraph("No alternative job role recommendations available.", styles["muted"])])
        )
    story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 10. AI-Assisted Improvement Suggestions (Optional)
    # -----------------------------------------------------------------------
    ai_roadmap = (gap_analysis or {}).get("ai_roadmap")
    if ai_roadmap and isinstance(ai_roadmap, str) and ai_roadmap.strip():
        ai_lines = [line.strip() for line in ai_roadmap.strip().splitlines() if line.strip()]
        ai_elements = [
            Paragraph(
                "<font size=8 color='#6d28d9'><b>AI-Assisted Bullet & Narrative Optimization (Advisory)</b></font>",
                styles["section_subheading"],
            ),
            Paragraph(
                "<font size=7 color='#64748b'>Supplementary AI guidance. "
                "Deterministic ATS scores and rankings remain unchanged.</font>",
                styles["muted"],
            ),
            Spacer(1, 3),
        ]
        for line in ai_lines:
            ai_elements.append(
                Paragraph(
                    f"<font color='#7c3aed'><b>•</b></font>  <font size=7.5 color='#334155'>{line}</font>",
                    styles["ai_body"],
                )
            )
        ai_card = Table([[ai_elements]], colWidths=[CONTENT_WIDTH], hAlign="LEFT")
        ai_card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), AI_BG),
            ("BOX", (0, 0), (-1, -1), 0.75, AI_BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        hdr_ai = _section_header("AI-Assisted Guidance", styles)
        story.append(KeepTogether([*hdr_ai, ai_card]))
        story.append(Spacer(1, 4))

    # -----------------------------------------------------------------------
    # 11. Footer Disclaimer Note
    # -----------------------------------------------------------------------
    story.append(Spacer(1, 8))
    story.append(HRFlowable(width=CONTENT_WIDTH, thickness=0.5, color=BORDER_LIGHT))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        f"<font size=7 color='#64748b'><i>This report was generated by <b>{BRAND_NAME}</b>. "
        "ATS scores are calculated using deterministic weighted algorithms "
        "(50% Skill Match + 30% Text Relevance + 20% Experience Match) "
        "and are never modified by AI features.</i></font>",
        styles["muted"],
    ))

    # -----------------------------------------------------------------------
    # Build Document
    # -----------------------------------------------------------------------
    pdf.build(story, onFirstPage=_draw_header_footer, onLaterPages=_draw_header_footer)

    return REPORT_FILE_PATH