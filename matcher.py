import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from functools import lru_cache
from sentence_transformers import SentenceTransformer

SKILL_WEIGHT = 0.50
TEXT_WEIGHT = 0.30
EXPERIENCE_WEIGHT = 0.20


@lru_cache(maxsize=1)
def get_semantic_model():
    return SentenceTransformer("all-MiniLM-L6-v2")


from skills import ALIAS_INDEX, SKILL_DATABASE


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

RESPONSIBILITY_HEADERS = [
    "responsibilities",
    "responsibility",
    "what you will do",
    "what you'll do",
    "role responsibilities",
    "key responsibilities",
    "duties",
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


def _skill_match_pattern(value):
    """Build a skill boundary pattern that avoids matching aliases inside skills."""
    return r"(?<![a-zA-Z0-9+#-])" + re.escape(value) + r"(?![a-zA-Z0-9+#-])"


def _iter_skill_variants():
    """Yield canonical skills and their unambiguous aliases."""
    for canonical_skill, metadata in SKILL_DATABASE.items():
        yield canonical_skill, canonical_skill

        for alias in metadata.get("aliases", []):
            if ALIAS_INDEX.get(alias) == [canonical_skill]:
                yield alias, canonical_skill


def _resolve_overlapping_mentions(mentions):
    """Prefer the longest canonical/alias match when skill mentions overlap."""
    resolved = []

    for mention in sorted(
        mentions,
        key=lambda item: (item[0], -(item[1] - item[0]), item[2]),
    ):
        start, end, skill = mention

        overlaps_existing = any(
            start < existing_end and end > existing_start
            for existing_start, existing_end, _ in resolved
        )

        if overlaps_existing:
            continue

        resolved.append((start, end, skill))

    return sorted(resolved)


def extract_skills(text):
    """
    Extract canonical skills from text using
    canonical names and aliases.
    """

    normalized_text = preprocess(text)
    mentions = []

    for variant, canonical_skill in _iter_skill_variants():
        normalized_variant = preprocess(variant)

        if not normalized_variant:
            continue

        pattern = _skill_match_pattern(normalized_variant)

        for match in re.finditer(pattern, normalized_text):
            mentions.append((match.start(), match.end(), canonical_skill))

    return {skill for _, _, skill in _resolve_overlapping_mentions(mentions)}


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
    """Find canonical skills and their positions in the normalized text."""

    normalized_text = _structure_normalize(text)

    mentions = []

    for variant, canonical_skill in _iter_skill_variants():
        normalized_variant = _structure_normalize(variant)

        if not normalized_variant:
            continue

        pattern = _skill_match_pattern(normalized_variant)

        for match in re.finditer(pattern, normalized_text):
            # Ignore skills that are inside parentheses.
            #
            # Example:
            # Node.js (TypeScript) or Go
            #
            # TypeScript is descriptive information about Node.js,
            # not another OR alternative.
            before = normalized_text[: match.start()]

            if before.count("(") > before.count(")"):
                continue

            mentions.append((match.start(), match.end(), canonical_skill))

    return _resolve_overlapping_mentions(mentions), normalized_text


def extract_alternative_requirements(text):
    """
    Detect alternative skill requirements.

    Examples:
        Python or Go
        AWS or GCP
        Node.js, TypeScript, Go, or Python
        Python / Go
        Node.js (TypeScript) or Go
        Terraform or CloudFormation
    """

    alternatives = []

    # Keep sentence / bullet boundaries separate.
    segments = re.split(r"(?<=[.!?])\s+|[;\n]+", text)

    for segment in segments:

        mentions, normalized_text = _find_skill_mentions(segment)

        if len(mentions) < 2:
            continue

        for index in range(1, len(mentions)):

            previous = mentions[index - 1]
            current = mentions[index]

            between = normalized_text[previous[1] : current[0]]

            # Explicit OR or slash.
            if not re.search(r"\bor\b|/", between):
                continue

            group = {previous[2], current[2]}

            # -------------------------------------------------
            # Extend backwards for:
            #
            # Python, TypeScript, Go, or Rust
            #
            # Node.js, TypeScript, Go or Python
            # -------------------------------------------------

            backward = index - 1

            while backward > 0:

                separator = normalized_text[
                    mentions[backward - 1][1] : mentions[backward][0]
                ]

                if not re.fullmatch(r"[\s,;/\-()]+", separator):
                    break

                group.add(mentions[backward - 1][2])

                backward -= 1

            # -------------------------------------------------
            # Extend forward for cases such as:
            #
            # Python or Go or Rust
            # -------------------------------------------------

            forward = index + 1

            while forward < len(mentions):

                separator = normalized_text[
                    mentions[forward - 1][1] : mentions[forward][0]
                ]

                if not re.fullmatch(r"[\s,;/\-()]+", separator):
                    break

                group.add(mentions[forward][2])

                forward += 1

            alternatives.append(frozenset(group))

    # ---------------------------------------------------------
    # Remove duplicate / overlapping alternatives
    # ---------------------------------------------------------

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


def _extract_parenthetical_or_skills(text):
    """Find skills inside parentheses within OR requirement segments."""
    ignored_skills = set()
    segments = re.split(r"(?<=[.!?])\s+|[;\n]+", text)

    for segment in segments:
        if not re.search(r"\bor\b|/", segment):
            continue

        for parenthetical_text in re.findall(r"\(([^)]*)\)", segment):
            ignored_skills.update(extract_skills(parenthetical_text))

    return ignored_skills


def _extract_job_section_skills(text):
    """Extract JD skills without treating OR parentheticals as requirements."""
    return extract_skills(text) - _extract_parenthetical_or_skills(text)


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


def _find_section_ranges(text):
    """Find JD section ranges for required, optional, and responsibility text."""
    section_headers = {
        "required": REQUIRED_HEADERS,
        "optional": OPTIONAL_HEADERS,
        "responsibilities": RESPONSIBILITY_HEADERS,
    }
    matches = []

    for section_name, headers in section_headers.items():
        for header in headers:
            for match in re.finditer(_skill_match_pattern(header), text):
                matches.append(
                    {
                        "section": section_name,
                        "start": match.start(),
                        "end": match.end(),
                        "header": header,
                    }
                )

    matches.sort(key=lambda item: (item["start"], -(item["end"] - item["start"])))

    deduplicated = []
    seen_starts = set()

    for match in matches:
        if match["start"] in seen_starts:
            continue

        deduplicated.append(match)
        seen_starts.add(match["start"])

    sections = {
        "general": text[: deduplicated[0]["start"]] if deduplicated else text,
        "required": "",
        "optional": "",
        "responsibilities": "",
    }

    for index, match in enumerate(deduplicated):
        next_start = (
            deduplicated[index + 1]["start"]
            if index + 1 < len(deduplicated)
            else len(text)
        )
        sections[match["section"]] += " " + text[match["end"] : next_start]

    return sections


def parse_job_description(job_text):
    """
    Parse a job description into structured requirements.
    """

    text = _structure_normalize(job_text)
    sections = _find_section_ranges(text)

    general_text = sections["general"]
    required_text = sections["required"]
    optional_text = sections["optional"]
    responsibilities_text = sections["responsibilities"]

    # -----------------------------------------
    # Extract skills
    # -----------------------------------------

    general_skills = _extract_job_section_skills(
        general_text
    )

    required_skills = _extract_job_section_skills(
        required_text
    )

    optional_skills = _extract_job_section_skills(
        optional_text
    )

    responsibility_skills = _extract_job_section_skills(
        responsibilities_text
    )

    # Responsibilities are tracked separately and still count as
    # general JD skills for the existing scoring model.
    general_skills = general_skills | responsibility_skills

    # -----------------------------------------
    # If no explicit required section exists,
    # treat general skills as required.
    # -----------------------------------------

    if not required_text:
        required_skills = set(general_skills)

    # -----------------------------------------
    # All skills
    # -----------------------------------------

    all_skills = (
        general_skills
        | required_skills
        | optional_skills
        | responsibility_skills
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

    responsibility_alternatives = (
        extract_alternative_requirements(
            responsibilities_text
        )
    )

    general_alternatives = (
        general_alternatives
        + responsibility_alternatives
    )

    # If there is no explicit required section,
    # general alternatives are required.
    if not required_text:
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
        "nice_to_have": optional_skills,
        "responsibilities": responsibility_skills,
        "all": all_skills,

        "required_alternatives":
            required_alternatives,

        "optional_alternatives":
            optional_alternatives,

        "general_alternatives":
            general_alternatives,

        "responsibility_alternatives":
            responsibility_alternatives,

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
    """
    Calculate hybrid semantic + lexical similarity between resume and job description.
    """

    resume = preprocess(resume)
    job = preprocess(job)

    if not resume or not job:
        return 0.0

    # -----------------------------------------
    # 1. TF-IDF lexical similarity
    # -----------------------------------------
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        sublinear_tf=True,
    )

    tfidf_matrix = vectorizer.fit_transform([resume, job])

    tfidf_score = cosine_similarity(
        tfidf_matrix[0],
        tfidf_matrix[1],
    )[
        0
    ][0]

    # -----------------------------------------
    # 2. Semantic similarity
    # -----------------------------------------
    model = get_semantic_model()

    embeddings = model.encode(
        [resume, job],
        normalize_embeddings=True,
        batch_size=2,
        show_progress_bar=False,
    )

    semantic_score = cosine_similarity(
        [embeddings[0]],
        [embeddings[1]],
    )[
        0
    ][0]

    # -----------------------------------------
    # 3. Hybrid score
    # -----------------------------------------
    hybrid_score = 0.70 * semantic_score + 0.30 * tfidf_score

    hybrid_score = max(0.0, min(1.0, hybrid_score))

    return round(hybrid_score * 100, 2)


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

    missing_skills = list(dict.fromkeys(missing_skills))

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

    if not resume or not resume.strip():
        return 0

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
