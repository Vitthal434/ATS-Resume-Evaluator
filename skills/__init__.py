from .programming import PROGRAMMING_SKILLS
from .frontend import FRONTEND_SKILLS
from .backend import BACKEND_SKILLS
from .database import DATABASE_SKILLS
from .cloud import CLOUD_SKILLS
from .devops import DEVOPS_SKILLS
from .version_control import VERSION_CONTROL_SKILLS
from .ai_ml import AI_ML_SKILLS
from .mlops import MLOPS_SKILLS
from .testing import TESTING_SKILLS
from .security import SECURITY_SKILLS
from .messaging import MESSAGING_SKILLS
from .design import DESIGN_SKILLS
from .build_tools import BUILD_TOOLS_SKILLS

# ============================================================
# BUILD MASTER DATABASE
# ============================================================

SKILL_DATABASE = {}

for database in (
    PROGRAMMING_SKILLS,
    FRONTEND_SKILLS,
    BACKEND_SKILLS,
    DATABASE_SKILLS,
    CLOUD_SKILLS,
    DEVOPS_SKILLS,
    VERSION_CONTROL_SKILLS,
    AI_ML_SKILLS,
    MLOPS_SKILLS,
    TESTING_SKILLS,
    SECURITY_SKILLS,
    MESSAGING_SKILLS,
    DESIGN_SKILLS,
    BUILD_TOOLS_SKILLS,
):
    SKILL_DATABASE.update(database)


# ============================================================
# DEFAULT METADATA
# ============================================================

DEFAULT_PRIORITY = "medium"


# ============================================================
# NORMALIZE SKILL RECORDS
# ============================================================


def _normalize_skill_database(database):
    normalized = {}

    for canonical, metadata in database.items():

        canonical = canonical.strip().lower()

        if not isinstance(metadata, dict):
            metadata = {}

        record = dict(metadata)

        # ----------------------------------------------------
        # Required fields
        # ----------------------------------------------------

        record.setdefault("display", canonical.title())

        record.setdefault("category", "general")

        record.setdefault("aliases", [])

        record.setdefault("priority", DEFAULT_PRIORITY)

        record.setdefault("related", [])

        # ----------------------------------------------------
        # Normalize aliases
        # ----------------------------------------------------

        aliases = []

        for alias in record.get("aliases", []):

            if not isinstance(alias, str):
                continue

            alias = alias.strip().lower()

            if not alias:
                continue

            # Canonical name should never be its own alias.
            if alias == canonical:
                continue

            if alias not in aliases:
                aliases.append(alias)

        record["aliases"] = aliases

        # ----------------------------------------------------
        # Normalize related skills
        # ----------------------------------------------------

        related = []

        for skill in record.get("related", []):

            if not isinstance(skill, str):
                continue

            skill = skill.strip().lower()

            if not skill:
                continue

            if skill == canonical:
                continue

            if skill not in related:
                related.append(skill)

        record["related"] = related

        normalized[canonical] = record

    return normalized


SKILL_DATABASE = _normalize_skill_database(SKILL_DATABASE)


# ============================================================
# ALIAS COLLISION HANDLING
# ============================================================


def _build_alias_index(database):
    alias_index = {}

    for canonical, metadata in database.items():

        for alias in metadata.get("aliases", []):

            alias_index.setdefault(alias, []).append(canonical)

    return alias_index


ALIAS_INDEX = _build_alias_index(SKILL_DATABASE)


# ============================================================
# REMOVE AMBIGUOUS ALIASES
# ============================================================
#
# If an alias points to multiple canonical skills, we remove
# that alias instead of allowing unpredictable matching.
#
# Example:
#
# application security
#     → system security
#     → web security
#
# This is safer than randomly choosing one.
# ============================================================

for alias, canonical_skills in ALIAS_INDEX.items():

    if len(canonical_skills) <= 1:
        continue

    for canonical in canonical_skills:

        aliases = SKILL_DATABASE[canonical]["aliases"]

        SKILL_DATABASE[canonical]["aliases"] = [
            value for value in aliases if value != alias
        ]


# ============================================================
# FINAL ALIAS INDEX
# ============================================================

ALIAS_INDEX = _build_alias_index(SKILL_DATABASE)
