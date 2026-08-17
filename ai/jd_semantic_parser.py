"""
ResumeIQ — AI Job Description Semantic Parser
Parses complex, ambiguous job descriptions into a structured, validated semantic schema.
Encapsulates anti-hallucination rules and fallback schema handling.

Uses the configured AI provider (ai.provider) — defaults to local open-source model.
AI_PROVIDER=local (default) or AI_PROVIDER=gemini
"""

import os
import json
from typing import Dict, Any

from ai.provider import is_ai_available, call_ai


SYSTEM_PROMPT = """
You are an expert ATS Technical Recruiter and Job Description Parser.
Your task is to analyze a raw job description and convert it into a structured, validated JSON representation.

STRICT NON-HALLUCINATION RULES:
1. NEVER invent skills, technologies, tools, certifications, or experience requirements not explicitly stated or directly implied in the job description.
2. DO NOT add complementary technologies. (Example: If the JD says "React", DO NOT automatically add "Redux", "Next.js", or "TypeScript").
3. For alternative/OR requirements (e.g. "Python or Go", "React/Angular/Vue", "AWS or GCP"), group them in "alternative_requirements" as a list of alternatives (e.g. ["python", "go"]).
4. Differentiate strictly between "required_skills" and "preferred_skills" (nice-to-have, bonus, plus).
5. Extract explicit years of experience and domain (e.g., "3+ years of backend development" -> years: 3, domain: "backend development").

Return your output strictly as valid JSON matching this schema:
{
  "job_title": "Detected job title or Software Engineering Role",
  "required_skills": [
    {"skill": "python", "importance": "required", "evidence": "Must have strong Python experience"}
  ],
  "alternative_requirements": [
    {"group": ["python", "go"], "requirement_type": "required"}
  ],
  "preferred_skills": [
    {"skill": "docker", "importance": "preferred", "evidence": "Experience with Docker is a plus"}
  ],
  "responsibilities": [
    "Develop and maintain RESTful web APIs"
  ],
  "experience_requirements": [
    {"requirement": "3+ years of backend development", "years": 3, "domain": "backend development"}
  ],
  "education_requirements": [
    "Bachelor's degree in Computer Science or equivalent"
  ],
  "certifications": [],
  "tools_and_platforms": ["AWS", "Docker", "PostgreSQL"],
  "domain_knowledge": ["distributed systems"],
  "soft_skills": ["communication", "problem solving"]
}
"""


def _get_empty_schema(job_title: str = "Software Engineering Role") -> Dict[str, Any]:
    """Return default empty schema structure for safe fallback."""
    return {
        "job_title": job_title,
        "required_skills": [],
        "alternative_requirements": [],
        "preferred_skills": [],
        "responsibilities": [],
        "experience_requirements": [],
        "education_requirements": [],
        "certifications": [],
        "tools_and_platforms": [],
        "domain_knowledge": [],
        "soft_skills": []
    }


def validate_semantic_schema(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Ensure all expected fields exist in parsed JSON output with correct types."""
    schema = _get_empty_schema()
    if not isinstance(parsed_data, dict):
        return schema

    schema["job_title"] = str(parsed_data.get("job_title", "Software Engineering Role")).strip()

    for key in [
        "required_skills",
        "alternative_requirements",
        "preferred_skills",
        "responsibilities",
        "experience_requirements",
        "education_requirements",
        "certifications",
        "tools_and_platforms",
        "domain_knowledge",
        "soft_skills"
    ]:
        val = parsed_data.get(key, [])
        if isinstance(val, list):
            schema[key] = val
        else:
            schema[key] = []

    return schema


def parse_job_description(job_description: str) -> Dict[str, Any]:
    """
    Semantically parse raw job description text using the configured AI provider.
    Returns a dictionary containing 'available', 'error', and 'analysis'.
    Falls back safely if AI provider is unavailable or call fails.

    Does not modify or influence deterministic ATS scoring in any way.
    """
    if not is_ai_available():
        return {
            "available": False,
            "error": (
                "AI service is not available. Install torch and transformers for local AI, "
                "or set AI_PROVIDER=gemini with a valid GEMINI_API_KEY."
            ),
            "analysis": _get_empty_schema()
        }

    if not job_description or not job_description.strip():
        return {
            "available": True,
            "error": "Job description is required.",
            "analysis": _get_empty_schema()
        }

    user_prompt = f"""{SYSTEM_PROMPT}

RAW JOB DESCRIPTION TO PARSE:
{job_description[:2500]}

Convert this job description into the structured JSON schema defined above.
"""

    try:
        jd_max_tokens = int(os.environ.get("AI_JD_MAX_TOKENS", "384"))
        raw_response = call_ai(user_prompt, max_tokens=jd_max_tokens)

        clean_json = raw_response.strip()
        if clean_json.startswith("```json"):
            clean_json = clean_json[7:]
        if clean_json.startswith("```"):
            clean_json = clean_json[3:]
        if clean_json.endswith("```"):
            clean_json = clean_json[:-3]
        clean_json = clean_json.strip()

        parsed = json.loads(clean_json)
        validated_analysis = validate_semantic_schema(parsed)

        return {
            "available": True,
            "error": None,
            "analysis": validated_analysis
        }
    except json.JSONDecodeError as e:
        return {
            "available": True,
            "error": f"Failed to parse AI response as valid JSON: {str(e)}",
            "analysis": _get_empty_schema()
        }
    except Exception as e:
        return {
            "available": True,
            "error": str(e),
            "analysis": _get_empty_schema()
        }
