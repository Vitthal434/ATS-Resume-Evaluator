import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

BRAND_NAME = "ATS Resume Evaluator"
REPORT_FILE_PATH = os.path.join("reports", "ATS_Report.pdf")

PRIMARY_COLOR = colors.HexColor("#1d4ed8")
TEXT_COLOR = colors.HexColor("#172033")
MUTED_COLOR = colors.HexColor("#64748b")
BORDER_COLOR = colors.HexColor("#dbe3ef")
SURFACE_COLOR = colors.HexColor("#f8fafc")


def _build_table(data, column_widths=None, header=True):
    """Create a consistently styled report table."""
    table = Table(data, colWidths=column_widths, hAlign="LEFT")
    table_style = [
        ("GRID", (0, 0), (-1, -1), 0.5, BORDER_COLOR),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, -1), TEXT_COLOR),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SURFACE_COLOR]),
    ]

    if header:
        table_style.extend(
            [
                ("BACKGROUND", (0, 0), (-1, 0), PRIMARY_COLOR),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ]
        )

    table.setStyle(TableStyle(table_style))
    return table


def _add_section_title(story, title, styles):
    """Add a section heading with consistent spacing."""
    story.append(Spacer(1, 14))
    story.append(Paragraph(f"<b>{title}</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))


def _add_list_items(story, items, empty_message, marker, styles):
    """Add simple list rows to the PDF story."""
    if items:
        for item in items:
            story.append(Paragraph(f"{marker} {item}", styles["Normal"]))
    else:
        story.append(Paragraph(empty_message, styles["Normal"]))


def format_skill(skill):
    if not skill:
        return ""
    if " or " in skill:
        return " or ".join(format_skill(part) for part in skill.split(" or "))
    mapping = {
        "aws": "AWS",
        "gcp": "GCP",
        "api": "API",
        "rest api": "REST API",
        "html": "HTML",
        "css": "CSS",
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "github": "GitHub",
        "git": "Git",
        "oop": "OOP",
        "dsa": "DSA",
        "nlp": "NLP",
        "natural language processing": "Natural Language Processing",
        "ai": "AI",
        "ml": "ML",
        "c++": "C++",
        "power bi": "Power BI",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "react.js": "React.js",
        "vue.js": "Vue.js",
        "node.js": "Node.js",
    }
    return mapping.get(skill.lower(), skill.title())


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
):
    """
    Generate the ATS analysis PDF and return its file path.
    """
    os.makedirs("reports", exist_ok=True)

    formatted_matched = [format_skill(s) for s in (matched or [])]
    formatted_missing = [format_skill(s) for s in (missing or [])]

    pdf = SimpleDocTemplate(
        REPORT_FILE_PATH,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.65 * inch,
    )
    styles = getSampleStyleSheet()
    styles["Title"].textColor = PRIMARY_COLOR
    styles["Title"].fontSize = 22
    styles["Title"].leading = 28
    styles["Heading2"].textColor = TEXT_COLOR
    styles["Heading2"].fontSize = 14
    styles["Heading2"].leading = 18
    styles["Normal"].textColor = TEXT_COLOR
    styles["Normal"].fontSize = 10
    styles["Normal"].leading = 15
    styles["Italic"].textColor = MUTED_COLOR

    story = []

    story.append(Paragraph(f"<b>{BRAND_NAME}</b>", styles["Title"]))
    story.append(
        Paragraph("Professional ATS Resume Analysis Report", styles["Heading2"])
    )
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "A concise summary of resume alignment, skill coverage, "
            "experience relevance, and recommended job roles.",
            styles["Normal"],
        )
    )
    story.append(Spacer(1, 18))

    _add_section_title(story, "Score Summary", styles)
    score_table = [
        ["ATS Score", f"{score}%"],
        ["Category", category],
        ["Skill Score", f"{skill_score}%"],
        ["Text Similarity", f"{text_similarity}%"],
        ["Experience Score", f"{experience_score}%"],
    ]
    story.append(
        _build_table(score_table, column_widths=[2.3 * inch, 3.6 * inch])
    )

    _add_section_title(story, "Matched Skills", styles)
    _add_list_items(story, formatted_matched, "No matched skills found.", "+", styles)

    _add_section_title(story, "Missing Skills", styles)
    _add_list_items(story, formatted_missing, "No missing skills.", "-", styles)

    _add_section_title(story, "Suggestions", styles)
    _add_list_items(story, suggestions, "No suggestions available.", "-", styles)

    _add_section_title(story, "Recommended Jobs", styles)
    if recommended_jobs:
        job_table = [["Job Role", "Match Score"]]

        for job in recommended_jobs:
            job_table.append(
                [
                    job["job"],
                    f'{job["score"]}%',
                ]
            )

        story.append(
            _build_table(
                job_table,
                column_widths=[4.0 * inch, 1.9 * inch],
            )
        )
    else:
        story.append(
            Paragraph("No recommendations available.", styles["Normal"])
        )

    story.append(Spacer(1, 24))
    story.append(
        Paragraph(
            f"<b>Generated by {BRAND_NAME}</b>",
            styles["Italic"],
        )
    )

    pdf.build(story)

    return REPORT_FILE_PATH