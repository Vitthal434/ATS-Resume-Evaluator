import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

SKILL_WEIGHT = 0.50
TEXT_WEIGHT = 0.30
EXPERIENCE_WEIGHT = 0.20

from skills import SKILL_DATABASE


def preprocess(text):
    """Normalize text while preserving skill-identifying characters."""
    text = text.lower()

    # Normalize common punctuation variations
    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")

    # Normalize dots used in technology names
    text = re.sub(r"\bnode\s*\.?\s*js\b", "node.js", text)
    text = re.sub(r"\breact\s*\.?\s*js\b", "react.js", text)
    text = re.sub(r"\bvue\s*\.?\s*js\b", "vue.js", text)

    # Keep letters, numbers, spaces and common skill characters
    text = re.sub(r"[^a-zA-Z0-9+#.\- ]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


REQUIRED_HEADERS = [
    "required skills",
    "required qualifications",
    "minimum qualifications",
    "minimum requirements",
    "requirements",
    "required",
    "must have",
    "mandatory skills",
    "mandatory qualifications",
]

OPTIONAL_HEADERS = [
    "preferred qualifications",
    "preferred skills",
    "preferred",
    "nice to have",
    "nice-to-have",
    "bonus",
    "bonuses",
    "good to have",
    "good-to-have",
    "desired skills",
    "additional qualifications",
]

EXPERIENCE_PATTERNS = [
    r"(\d+)\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",
    r"(\d+)\+?\s*years?\s+(?:of\s+)?experience",
    r"minimum\s+of\s+(\d+)\s+years?",
    r"at\s+least\s+(\d+)\s+years?",
]

EDUCATION_KEYWORDS = [
    "bachelor",
    "bachelor's",
    "b.s.",
    "b.sc.",
    "b.tech",
    "b.e.",
    "master",
    "master's",
    "m.s.",
    "m.sc.",
    "m.tech",
    "m.e.",
    "phd",
    "ph.d.",
    "doctorate",
]


def extract_skills(text):
    """
    Extract canonical skills from text using
    canonical names and aliases.
    """

    normalized_text = preprocess(text)
    found_skills = set()

    for canonical_skill, metadata in SKILL_DATABASE.items():

        # Normalize canonical skill
        canonical_normalized = preprocess(canonical_skill)

        # Match canonical skill
        pattern = r"(?<!\w)" + re.escape(canonical_normalized) + r"(?!\w)"

        if re.search(pattern, normalized_text):
            found_skills.add(canonical_skill)
            continue

        # Match aliases
        for alias in metadata.get("aliases", []):

            alias_normalized = preprocess(alias)

            if not alias_normalized:
                continue

            pattern = r"(?<!\w)" + re.escape(alias_normalized) + r"(?!\w)"

            if re.search(pattern, normalized_text):
                found_skills.add(canonical_skill)
                break

    return found_skills


def _structure_normalize(text):
    """Normalize text while preserving punctuation used for requirement parsing."""

    text = text.lower()

    text = text.replace("–", "-")
    text = text.replace("—", "-")
    text = text.replace("’", "'")

    text = re.sub(r"\bnode\s*\.?\s*js\b", "node.js", text)
    text = re.sub(r"\breact\s*\.?\s*js\b", "react.js", text)
    text = re.sub(r"\bvue\s*\.?\s*js\b", "vue.js", text)

    return text


def _find_skill_mentions(text):
    """Find canonical skills and their positions in the original text."""

    normalized_text = _structure_normalize(text)

    mentions = {}

    for canonical_skill, metadata in SKILL_DATABASE.items():

        variants = [canonical_skill, *metadata.get("aliases", [])]

        for variant in variants:

            variant = _structure_normalize(variant)

            if not variant:
                continue

            pattern = r"(?<!\w)" + re.escape(variant) + r"(?!\w)"

            for match in re.finditer(pattern, normalized_text):

                # Ignore skills mentioned inside parentheses.
                # Example:
                # Node.js (TypeScript) or Go
                if normalized_text[: match.start()].count("(") > normalized_text[
                    : match.start()
                ].count(")"):
                    continue

                key = (match.start(), match.end())

                current = mentions.get(key)

                if current is None or len(variant) > current[0]:
                    mentions[key] = (len(variant), canonical_skill)

    results = [(start, end, value[1]) for (start, end), value in mentions.items()]

    return sorted(results), normalized_text


def extract_alternative_requirements(text):
    """
    Detect OR / alternative skill requirements.

    Examples:

        Python or Go
        AWS or GCP
        Node.js, TypeScript, Go, or Python
        Python / Go
    """

    alternatives = []

    # Keep sentence boundaries so unrelated requirements
    # are not accidentally merged.
    segments = re.split(r"(?<=[.!?])\s+|[;\n]+", text)

    for segment in segments:

        mentions, normalized_text = _find_skill_mentions(segment)

        if len(mentions) < 2:
            continue

        for index in range(1, len(mentions)):

            previous = mentions[index - 1]
            current = mentions[index]

            between = normalized_text[previous[1] : current[0]]

            # Detect explicit OR or slash alternatives.
            if not re.search(r"\bor\b|/", between):
                continue

            group = {previous[2], current[2]}

            # Extend:
            #
            # Python, TypeScript, Go, or Rust
            #
            # from {Go, Rust}
            # to {Python, TypeScript, Go, Rust}

            backward = index - 1

            while backward > 0:

                separator = normalized_text[
                    mentions[backward - 1][1] : mentions[backward][0]
                ]

                # Don't cross parentheses.
                if "(" in separator or ")" in separator:
                    break

                # Only extend across list separators.
                if not re.fullmatch(r"[\s,;/\-]+", separator):
                    break

                group.add(mentions[backward - 1][2])

                backward -= 1

            alternatives.append(frozenset(group))

    # Remove duplicate / overlapping groups.
    unique = []

    for group in alternatives:

        if group in unique:
            continue

        merged = False

        for index, existing in enumerate(unique):

            if group & existing:

                unique[index] = frozenset(existing | group)

                merged = True
                break

        if not merged:
            unique.append(group)

    return unique


def extract_experience_requirements(text):
    """Extract minimum years of experience from a JD."""

    years_found = []

    for pattern in EXPERIENCE_PATTERNS:
        matches = re.findall(pattern, text, flags=re.IGNORECASE)

        for match in matches:
            try:
                years_found.append(int(match))
            except ValueError:
                continue

    return max(years_found, default=0)


def extract_education_requirements(text):
    """Extract education requirements mentioned in a JD."""

    normalized_text = preprocess(text)

    found = set()

    for keyword in EDUCATION_KEYWORDS:
        normalized_keyword = preprocess(keyword)

        if normalized_keyword in normalized_text:
            found.add(keyword)

    return sorted(found)

def parse_job_description(job_text):
    """
    Parse a job description into structured requirements.
    """

    text = preprocess(job_text)

    # -----------------------------------------
    # Locate optional section
    # -----------------------------------------

    optional_index = len(text)

    for header in OPTIONAL_HEADERS:
        index = text.find(header)

        if index != -1:
            optional_index = min(
                optional_index,
                index
            )

    # -----------------------------------------
    # Locate required section
    # -----------------------------------------

    required_index = None

    for header in REQUIRED_HEADERS:
        index = text.find(header)

        if index != -1:
            if required_index is None:
                required_index = index
            else:
                required_index = min(
                    required_index,
                    index
                )

    # -----------------------------------------
    # Split sections
    # -----------------------------------------

    if required_index is not None:

        general_text = text[:required_index]

        required_text = text[
            required_index:optional_index
        ]

    else:

        general_text = text
        required_text = ""

    # -----------------------------------------
    # Optional section
    # -----------------------------------------

    if optional_index < len(text):
        optional_text = text[optional_index:]
    else:
        optional_text = ""

    # -----------------------------------------
    # Extract skills
    # -----------------------------------------

    general_skills = extract_skills(
        general_text
    )

    required_skills = extract_skills(
        required_text
    )

    optional_skills = extract_skills(
        optional_text
    )

    # -----------------------------------------
    # If no explicit required section exists,
    # treat general skills as required.
    # -----------------------------------------

    if required_index is None:
        required_skills = set(general_skills)

    # -----------------------------------------
    # All skills
    # -----------------------------------------

    all_skills = (
        general_skills
        | required_skills
        | optional_skills
    )

    # -----------------------------------------
    # OR alternatives
    # -----------------------------------------

    required_alternatives = (
        extract_alternative_requirements(
            required_text
        )
    )

    optional_alternatives = (
        extract_alternative_requirements(
            optional_text
        )
    )

    general_alternatives = (
        extract_alternative_requirements(
            general_text
        )
    )

    # If there is no explicit required section,
    # general alternatives are required.
    if required_index is None:
        required_alternatives = list(
            general_alternatives
        )

    # -----------------------------------------
    # Experience
    # -----------------------------------------

    experience_years = (
        extract_experience_requirements(text)
    )

    # -----------------------------------------
    # Education
    # -----------------------------------------

    education = (
        extract_education_requirements(text)
    )

    return {
        "general": general_skills,
        "required": required_skills,
        "optional": optional_skills,
        "all": all_skills,

        "required_alternatives":
            required_alternatives,

        "optional_alternatives":
            optional_alternatives,

        "general_alternatives":
            general_alternatives,

        "alternatives":
            required_alternatives
            + optional_alternatives
            + general_alternatives,

        "experience_years":
            experience_years,

        "education":
            education,
    }


def calculate_weighted_skill_score(
    resume_skills,
    required_skills,
    optional_skills,
    general_skills=None,
    required_alternatives=None,
    optional_alternatives=None,
    general_alternatives=None,
):
    """
    Calculate weighted skill score.

    Required skill = 3 points
    General skill  = 2 points
    Optional skill = 1 point

    OR groups count as ONE requirement.
    """

    REQUIRED_WEIGHT = 3
    GENERAL_WEIGHT = 2
    OPTIONAL_WEIGHT = 1

    general_skills = general_skills or set()
    required_alternatives = required_alternatives or []
    optional_alternatives = optional_alternatives or []
    general_alternatives = general_alternatives or []

    matched_weight = 0
    total_weight = 0

    # ==========================================
    # REQUIRED OR GROUPS
    # ==========================================

    required_grouped = set()

    for group in required_alternatives:

        required_grouped.update(group)

        total_weight += REQUIRED_WEIGHT

        if resume_skills & set(group):
            matched_weight += REQUIRED_WEIGHT

    # ==========================================
    # REQUIRED INDIVIDUAL SKILLS
    # ==========================================

    for skill in required_skills:

        if skill in required_grouped:
            continue

        total_weight += REQUIRED_WEIGHT

        if skill in resume_skills:
            matched_weight += REQUIRED_WEIGHT

    # ==========================================
    # GENERAL OR GROUPS
    # ==========================================

    general_grouped = set()

    for group in general_alternatives:

        general_grouped.update(group)

        total_weight += GENERAL_WEIGHT

        if resume_skills & set(group):
            matched_weight += GENERAL_WEIGHT

    # ==========================================
    # GENERAL INDIVIDUAL SKILLS
    # ==========================================

    for skill in general_skills:

        if skill in general_grouped:
            continue

        if skill in required_skills:
            continue

        total_weight += GENERAL_WEIGHT

        if skill in resume_skills:
            matched_weight += GENERAL_WEIGHT

    # ==========================================
    # OPTIONAL OR GROUPS
    # ==========================================

    optional_grouped = set()

    for group in optional_alternatives:

        optional_grouped.update(group)

        total_weight += OPTIONAL_WEIGHT

        if resume_skills & set(group):
            matched_weight += OPTIONAL_WEIGHT

    # ==========================================
    # OPTIONAL INDIVIDUAL SKILLS
    # ==========================================

    for skill in optional_skills:

        if skill in optional_grouped:
            continue

        total_weight += OPTIONAL_WEIGHT

        if skill in resume_skills:
            matched_weight += OPTIONAL_WEIGHT

    if total_weight == 0:
        return 0

    return round((matched_weight / total_weight) * 100, 2)


def calculate_text_similarity(resume, job):
    """Calculate TF-IDF cosine similarity between resume and job description."""
    documents = [resume, job]
    vectorizer = TfidfVectorizer(stop_words="english")
    tfidf_matrix = vectorizer.fit_transform(documents)
    similarity = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])[0][0]

    return round(similarity * 100, 2)


def calculate_skill_match(resume, job):
    """
    Compare resume skills against structured JD requirements.
    """

    resume_skills = extract_skills(resume)

    job_data = parse_job_description(job)

    required_skills = job_data["required"]
    optional_skills = job_data["optional"]
    general_skills = job_data["general"]

    required_alternatives = job_data["required_alternatives"]

    optional_alternatives = job_data["optional_alternatives"]

    general_alternatives = job_data["general_alternatives"]

    all_job_skills = job_data["all"]

    if not all_job_skills:
        return 0, [], []

    # ==========================================
    # MATCHED SKILLS
    # ==========================================

    matched_skills = sorted(resume_skills & all_job_skills)

    missing_skills = []

    # ==========================================
    # REQUIRED OR GROUPS
    # ==========================================

    required_grouped = set()

    for group in required_alternatives:

        required_grouped.update(group)

        if not (resume_skills & set(group)):

            missing_skills.append(" or ".join(sorted(group)))

    # ==========================================
    # REQUIRED INDIVIDUAL
    # ==========================================

    for skill in sorted(required_skills):

        if skill in required_grouped:
            continue

        if skill not in resume_skills:
            missing_skills.append(skill)

    # ==========================================
    # GENERAL OR GROUPS
    # ==========================================

    general_grouped = set()

    for group in general_alternatives:

        general_grouped.update(group)

        if not (resume_skills & set(group)):

            missing_skills.append(" or ".join(sorted(group)))

    # ==========================================
    # GENERAL INDIVIDUAL
    # ==========================================

    for skill in sorted(general_skills):

        if skill in general_grouped:
            continue

        if skill in required_skills:
            continue

        if skill not in resume_skills:
            missing_skills.append(skill)

    # ==========================================
    # OPTIONAL OR GROUPS
    # ==========================================

    optional_grouped = set()

    for group in optional_alternatives:

        optional_grouped.update(group)

        if not (resume_skills & set(group)):

            missing_skills.append(" or ".join(sorted(group)))

    # ==========================================
    # OPTIONAL INDIVIDUAL
    # ==========================================

    for skill in sorted(optional_skills):

        if skill in optional_grouped:
            continue

        if skill not in resume_skills:
            missing_skills.append(skill)

    # ==========================================
    # SCORE
    # ==========================================

    skill_score = calculate_weighted_skill_score(
        resume_skills,
        required_skills,
        optional_skills,
        general_skills,
        required_alternatives,
        optional_alternatives,
        general_alternatives,
    )

    return (
        skill_score,
        matched_skills,
        missing_skills,
    )


def experience_score(resume):
    """
    Estimate experience score from resume text.

    Supports:
    - 5 years
    - 5+ years
    - 6 months
    - 45 days
    - internships
    - projects
    """

    resume = resume.lower()

    # -------- Years --------
    year_match = re.search(r"(\d+)\s*\+?\s*years?", resume)
    if year_match:
        years = int(year_match.group(1))
        return min(70 + years * 6, 100)

    # -------- Months --------
    month_match = re.search(r"(\d+)\s*months?", resume)
    if month_match:
        months = int(month_match.group(1))
        years = months / 12
        return min(65 + years * 6, 80)

    # -------- Days --------
    day_match = re.search(r"(\d+)\s*days?", resume)
    if day_match:
        days = int(day_match.group(1))
        years = days / 365
        return min(60 + years * 6, 70)

    # -------- Student Experience --------
    student_keywords = [
        "intern",
        "internship",
        "project",
        "projects",
        "freelance",
        "research",
        "training",
        "hackathon",
        "certification",
    ]

    if any(keyword in resume for keyword in student_keywords):
        return 65

    # -------- No Experience --------
    return 50


def final_match_score(resume, job):
    """Calculate final ATS score and return detailed match results."""
    text_score = calculate_text_similarity(resume, job)
    skill_score, matched_skills, missing_skills = calculate_skill_match(resume, job)
    exp_score = experience_score(resume)
    final_score = round(
        (SKILL_WEIGHT * skill_score)
        + (TEXT_WEIGHT * text_score)
        + (EXPERIENCE_WEIGHT * exp_score),
        2,
    )

    suggestions = []

    if missing_skills:
        suggestions.append("Consider adding these skills: " + ", ".join(missing_skills))

    if exp_score < 60:
        suggestions.append("Highlight internships, projects or practical experience.")

    if final_score > 85:
        recommendation = "Excellent Fit"
    elif final_score > 70:
        recommendation = "Good Fit"
    elif final_score > 50:
        recommendation = "Fair Fit"
    else:
        recommendation = "Needs Improvement"

    return {
        "ats_score": final_score,
        "text_similarity": text_score,
        "skill_score": skill_score,
        "experience_score": exp_score,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "recommendation": recommendation,
        "suggestions": suggestions,
    }
