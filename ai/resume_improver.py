"""
ResumeIQ — AI Resume Bullet Optimizer
Parses resume bullet points, enforces strict non-hallucination ATS prompts,
and returns structured before-and-after improvements aligned with job description requirements.

Uses the configured AI provider (ai.provider) — defaults to local open-source model.
AI_PROVIDER=local (default) or AI_PROVIDER=gemini
"""

import os
import json
import re
from typing import List, Dict, Any

from ai.provider import is_ai_available, call_ai


SYSTEM_PROMPT = """
You are an expert ATS Resume Coach and technical recruiter.
Your task is to analyze resume bullet points against a job description and suggest ATS-optimized improvements.

STRICT NON-HALLUCINATION RULES:
1. NEVER invent or fabricate facts, metrics, percentages, dollar amounts, revenue, user counts, years of experience, job titles, or certifications.
2. If the original bullet lacks quantitative metrics, DO NOT make up fictional numbers. Focus on action verbs, technical clarity, and ATS keyword alignment.
3. Preserve all original technologies, frameworks, and achievements.
4. Align phrasing with terminology from the job description ONLY where supported by the original candidate bullet.
5. Avoid buzzword stuffing and maintain clear, professional, concise language.

Return your response strictly in valid JSON matching this schema:
{
  "improvements": [
    {
      "original": "Original bullet text",
      "improved": "ATS-optimized bullet text",
      "reason": "Clear explanation of why this revision improves ATS alignment",
      "keywords_added": ["keyword1", "keyword2"],
      "skills_referenced": ["skill1"],
      "impact_level": "High" | "Medium" | "Low",
      "confidence": 0.95
    }
  ]
}
"""


def extract_bullets(text: str) -> List[str]:
    """Extract bullet points or key work experience sentences from raw text."""
    if not text or not text.strip():
        return []

    lines = [line.strip() for line in text.split("\n") if line.strip()]
    bullets = []

    for line in lines:
        # Strip common leading bullet markers: -, *, •, 1., etc.
        cleaned = re.sub(r"^[\-\*\•\d+\.]+\s*", "", line).strip()
        # Keep lines that resemble work experience statements (between 25 and 300 chars)
        if 25 <= len(cleaned) <= 300:
            bullets.append(cleaned)

    # Return top 3 most relevant bullets to keep prompt focused, fast, and within generation budget
    return bullets[:3]


def improve_resume_bullets(
    resume_text: str,
    job_description: str,
    missing_skills: List[str] = None
) -> Dict[str, Any]:
    """
    Generate structured ATS bullet improvements for resume text against a job description.
    Returns dictionary with 'available', 'improvements', and 'error' status.

    Uses the configured AI provider (local by default, optional Gemini).
    Does not modify or influence deterministic ATS scoring in any way.
    """
    if not is_ai_available():
        return {
            "available": False,
            "error": (
                "AI service is not available. Install torch and transformers for local AI, "
                "or set AI_PROVIDER=gemini with a valid GEMINI_API_KEY."
            ),
            "improvements": []
        }

    bullets = extract_bullets(resume_text)
    if not bullets:
        return {
            "available": True,
            "error": "No bullet points or work experience statements could be extracted from the resume.",
            "improvements": []
        }

    missing_str = ", ".join(missing_skills) if missing_skills else "None identified"

    user_prompt = f"""{SYSTEM_PROMPT}

TARGET JOB DESCRIPTION:
{job_description[:1500]}

MISSING ATS SKILLS TO HIGHLIGHT (IF TRUTHFULLY APPLICABLE):
{missing_str}

RESUME BULLETS TO OPTIMIZE:
"""
    for idx, bullet in enumerate(bullets, 1):
        user_prompt += f"{idx}. {bullet}\n"

    user_prompt += "\nAnalyze these bullets and return the structured JSON improvements."

    try:
        bullet_max_tokens = int(os.environ.get("AI_BULLET_MAX_TOKENS", "512"))
        raw_response = call_ai(user_prompt, max_tokens=bullet_max_tokens)

        # Clean any markdown codeblock formatting if present
        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed = json.loads(clean_json)
        improvements = parsed.get("improvements", [])

        return {
            "available": True,
            "improvements": improvements,
            "error": None
        }
    except json.JSONDecodeError as e:
        return {
            "available": True,
            "error": f"Failed to parse AI response as valid JSON: {str(e)}",
            "improvements": []
        }
    except Exception as e:
        return {
            "available": True,
            "error": str(e),
            "improvements": []
        }
