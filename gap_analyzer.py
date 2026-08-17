"""
ResumeIQ — Stage 9.4 Intelligent Resume-Job Gap Analyzer
Consumes deterministic matcher output and classifies JD requirements into exact, partial, and missing categories.
Assigns priority levels (CRITICAL, HIGH, MEDIUM, LOW) and optionally enriches with Gemini AI roadmaps.
"""

from typing import Dict, Any, List, Set
from matcher import (
    extract_skills,
    parse_job_description,
    _evaluate_requirement_match,
    PARTIAL_MATCH_FACTOR,
)
from ai.gemini_provider import is_gemini_available, call_gemini_api


def analyze_resume_job_gap(resume_text: str, job_text: str) -> Dict[str, Any]:
    """
    Perform deterministic gap analysis between resume text and job description text.
    Classifies requirements into EXACT, PARTIAL, and MISSING categories with priorities.
    Returns structured analysis dictionary.
    """
    if not job_text or not job_text.strip():
        return {
            "skill_coverage": {
                "exact_matches": 0,
                "partial_matches": 0,
                "missing": 0,
                "total_requirements": 0,
                "coverage_percentage": 0.0,
            },
            "exact_matches": [],
            "partial_matches": [],
            "missing_skills": [],
            "recommendations": [],
            "ai_roadmap": None,
        }

    resume_skills = extract_skills(resume_text) if (resume_text and resume_text.strip()) else set()
    job_data = parse_job_description(job_text)

    required_skills = job_data.get("required", set())
    optional_skills = job_data.get("optional", set())
    general_skills = job_data.get("general", set())

    required_alternatives = job_data.get("required_alternatives", [])
    optional_alternatives = job_data.get("optional_alternatives", [])
    general_alternatives = job_data.get("general_alternatives", [])

    exact_matches = []
    partial_matches = []
    missing_skills = []
    recommendations = []

    # Keep track of handled requirements to prevent duplicate classification
    required_grouped = set()

    # 1. REQUIRED OR-GROUPS
    for group in required_alternatives:
        required_grouped.update(group)
        group_label = " or ".join(sorted(group))
        ratio, exact_skill, related_skill = _evaluate_requirement_match(set(group), resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": exact_skill,
                "requirement": group_label,
                "category": "required"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": group_label,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "required",
                "priority": "HIGH"
            })
            recommendations.append({
                "skill": group_label,
                "priority": "HIGH",
                "reason": f"Partial match via {related_skill}. Upgrade to explicit {group_label} proficiency."
            })
        else:
            missing_skills.append({
                "skill": group_label,
                "category": "required",
                "priority": "CRITICAL"
            })
            recommendations.append({
                "skill": group_label,
                "priority": "CRITICAL",
                "reason": f"Required skill ({group_label}) is completely missing."
            })

    # 2. REQUIRED INDIVIDUAL SKILLS
    for skill in sorted(required_skills):
        if skill in required_grouped:
            continue

        ratio, exact_skill, related_skill = _evaluate_requirement_match({skill}, resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": skill,
                "requirement": skill,
                "category": "required"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": skill,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "required",
                "priority": "HIGH"
            })
            recommendations.append({
                "skill": skill,
                "priority": "HIGH",
                "reason": f"Partial match via {related_skill}. Consider explicitly acquiring {skill}."
            })
        else:
            missing_skills.append({
                "skill": skill,
                "category": "required",
                "priority": "CRITICAL"
            })
            recommendations.append({
                "skill": skill,
                "priority": "CRITICAL",
                "reason": f"Required skill ({skill}) is completely missing."
            })

    # 3. GENERAL OR-GROUPS
    general_grouped = set()
    for group in general_alternatives:
        general_grouped.update(group)
        group_label = " or ".join(sorted(group))
        ratio, exact_skill, related_skill = _evaluate_requirement_match(set(group), resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": exact_skill,
                "requirement": group_label,
                "category": "general"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": group_label,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "general",
                "priority": "MEDIUM"
            })
            recommendations.append({
                "skill": group_label,
                "priority": "MEDIUM",
                "reason": f"Partial match via {related_skill} for general requirement."
            })
        else:
            missing_skills.append({
                "skill": group_label,
                "category": "general",
                "priority": "HIGH"
            })
            recommendations.append({
                "skill": group_label,
                "priority": "HIGH",
                "reason": f"General role requirement ({group_label}) is missing."
            })

    # 4. GENERAL INDIVIDUAL SKILLS
    for skill in sorted(general_skills):
        if skill in general_grouped or skill in required_skills:
            continue

        ratio, exact_skill, related_skill = _evaluate_requirement_match({skill}, resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": skill,
                "requirement": skill,
                "category": "general"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": skill,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "general",
                "priority": "MEDIUM"
            })
            recommendations.append({
                "skill": skill,
                "priority": "MEDIUM",
                "reason": f"Partial match via {related_skill} for general requirement."
            })
        else:
            missing_skills.append({
                "skill": skill,
                "category": "general",
                "priority": "HIGH"
            })
            recommendations.append({
                "skill": skill,
                "priority": "HIGH",
                "reason": f"General role requirement ({skill}) is missing."
            })

    # 5. OPTIONAL / PREFERRED OR-GROUPS & INDIVIDUAL SKILLS
    optional_grouped = set()
    for group in optional_alternatives:
        optional_grouped.update(group)
        group_label = " or ".join(sorted(group))
        ratio, exact_skill, related_skill = _evaluate_requirement_match(set(group), resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": exact_skill,
                "requirement": group_label,
                "category": "optional"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": group_label,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "optional",
                "priority": "LOW"
            })
        else:
            missing_skills.append({
                "skill": group_label,
                "category": "optional",
                "priority": "MEDIUM"
            })

    for skill in sorted(optional_skills):
        if skill in optional_grouped:
            continue

        ratio, exact_skill, related_skill = _evaluate_requirement_match({skill}, resume_skills)

        if ratio == 1.0:
            exact_matches.append({
                "skill": skill,
                "requirement": skill,
                "category": "optional"
            })
        elif ratio == PARTIAL_MATCH_FACTOR:
            partial_matches.append({
                "required_skill": skill,
                "candidate_skill": related_skill,
                "credit": PARTIAL_MATCH_FACTOR,
                "category": "optional",
                "priority": "LOW"
            })
        else:
            missing_skills.append({
                "skill": skill,
                "category": "optional",
                "priority": "MEDIUM"
            })

    # Calculate coverage metrics
    num_exact = len(exact_matches)
    num_partial = len(partial_matches)
    num_missing = len(missing_skills)
    total_reqs = num_exact + num_partial + num_missing

    effective_matches = num_exact + (num_partial * PARTIAL_MATCH_FACTOR)
    coverage_pct = round((effective_matches / total_reqs * 100), 1) if total_reqs > 0 else 0.0

    return {
        "skill_coverage": {
            "exact_matches": num_exact,
            "partial_matches": num_partial,
            "missing": num_missing,
            "total_requirements": total_reqs,
            "coverage_percentage": coverage_pct,
        },
        "exact_matches": exact_matches,
        "partial_matches": partial_matches,
        "missing_skills": missing_skills,
        "recommendations": recommendations,
        "ai_roadmap": None,
    }


def enhance_gap_analysis_with_ai(gap_analysis: Dict[str, Any], job_text: str) -> Dict[str, Any]:
    """
    Optionally enrich deterministic gap analysis with a Gemini AI improvement roadmap.
    Fails safely if GEMINI_API_KEY is missing or API call fails.
    """
    if not is_gemini_available():
        return gap_analysis

    recommendations = gap_analysis.get("recommendations", [])
    missing = [m.get("skill") for m in gap_analysis.get("missing_skills", [])]
    partial = [p.get("required_skill") for p in gap_analysis.get("partial_matches", [])]

    if not missing and not partial and not recommendations:
        gap_analysis["ai_roadmap"] = "Candidate already meets all extracted skill requirements!"
        return gap_analysis

    prompt = f"""
You are an expert technical career coach.
Review the following DETERMINISTIC skill gap analysis for a candidate applying to this job description.

JOB DESCRIPTION:
{job_text[:1200]}

DETERMINISTIC GAP ANALYSIS:
- Critical Missing Skills: {missing}
- Partial/Transferable Skills: {partial}

STRICT NON-HALLUCINATION RULES:
1. DO NOT change the skill match scores, ATS score, or classification.
2. DO NOT invent certifications, years of experience, or candidate accomplishments.
3. Provide a concise, 3-step prioritized learning roadmap focused strictly on addressing the missing and partial skills listed above.

Return a short, professional bulleted action plan.
"""

    try:
        raw_response = call_gemini_api(prompt, timeout=12)
        gap_analysis["ai_roadmap"] = raw_response.strip()
    except Exception as e:
        # Fallback cleanly without crashing
        gap_analysis["ai_roadmap"] = None

    return gap_analysis
