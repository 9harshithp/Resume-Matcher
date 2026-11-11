"""Skill synonyms and canonical technology aliases for ATS matching."""

from __future__ import annotations

import re
from typing import Final

# Canonical clusters of equivalent technical terms, abbreviations, and spellings.
# All entries are lowercased and stripped.
_EQUIVALENCE_CLUSTERS: Final[list[set[str]]] = [
    # Cloud Providers & Infrastructure
    {"amazon web services", "aws"},
    {"google cloud platform", "google cloud", "gcp"},
    {"microsoft azure", "azure"},
    {"kubernetes", "k8s"},
    {"docker", "containerization", "containers"},
    {"terraform", "tf"},
    {"continuous integration / continuous deployment", "continuous integration", "continuous deployment", "ci/cd", "cicd", "ci cd"},
    {"site reliability engineering", "site reliability engineer", "sre"},
    {"infrastructure as code", "iac"},

    # Programming Languages
    {"golang", "go"},
    {"typescript", "ts"},
    {"javascript", "js", "ecmascript"},
    {"python", "py", "python3"},
    {"c++", "cpp"},
    {"c#", "csharp", "c sharp"},
    {".net", "dotnet", "dot net", ".net core"},
    {"objective-c", "objc"},

    # Web & Frontend Frameworks
    {"react", "reactjs", "react.js"},
    {"next.js", "nextjs", "next"},
    {"node.js", "nodejs", "node"},
    {"vue.js", "vuejs", "vue"},
    {"angular", "angularjs"},
    {"tailwind css", "tailwindcss", "tailwind"},
    {"sass", "scss"},
    {"html5", "html"},
    {"css3", "css"},
    {"frontend", "front-end", "front end"},
    {"backend", "back-end", "back end"},
    {"fullstack", "full-stack", "full stack"},

    # Databases & Storage
    {"postgresql", "postgres"},
    {"mongodb", "mongo"},
    {"relational database", "relational databases", "rdbms"},
    {"nosql", "non-relational database", "non-relational databases"},
    {"microsoft sql server", "mssql", "sql server"},
    {"elasticsearch", "elastic search", "es"},

    # API & Architecture
    {"rest", "restful", "rest api", "restful api", "rest apis"},
    {"graphql", "gql"},
    {"microservices", "microservice architecture", "micro-services"},
    {"message queue", "message broker", "pub/sub", "publish-subscribe"},
    {"apache kafka", "kafka"},
    {"apache spark", "spark"},
    {"apache airflow", "airflow"},

    # AI & Data Science
    {"machine learning", "ml"},
    {"deep learning", "dl"},
    {"artificial intelligence", "ai"},
    {"generative ai", "genai", "gen ai"},
    {"large language models", "large language model", "llm", "llms"},
    {"natural language processing", "nlp"},
    {"computer vision", "cv"},
    {"scikit-learn", "sklearn"},
    {"tensorflow", "tf"},
    {"pytorch", "torch"},

    # Software Engineering Practices & QA
    {"quality assurance", "qa"},
    {"test-driven development", "tdd"},
    {"behavior-driven development", "bdd"},
    {"object-oriented programming", "oop"},
    {"user experience", "ux"},
    {"user interface", "ui"},
    {"extract transform load", "etl"},
]

# Fast lookup map: term -> set of all equivalent terms (including itself)
_ALIAS_LOOKUP: dict[str, set[str]] = {}
for cluster in _EQUIVALENCE_CLUSTERS:
    for term in cluster:
        norm = term.strip().lower()
        if norm in _ALIAS_LOOKUP:
            _ALIAS_LOOKUP[norm].update(cluster)
        else:
            _ALIAS_LOOKUP[norm] = set(cluster)


def normalize_term(term: str) -> str:
    """Normalize a skill or keyword term by lowercasing and collapsing whitespace."""
    return re.sub(r"\s+", " ", term.strip().lower())


def get_skill_aliases(term: str) -> set[str]:
    """Return all known aliases and equivalent representations for a given skill or keyword.
    
    If the term is not in the equivalence dictionary, returns a set containing the normalized term
    and automatic variants (e.g. 'foo.js' <-> 'foojs', 'foo-bar' <-> 'foo bar').
    """
    normalized = normalize_term(term)
    if not normalized:
        return set()

    aliases = set()
    if normalized in _ALIAS_LOOKUP:
        aliases.update(_ALIAS_LOOKUP[normalized])
    else:
        aliases.add(normalized)

    # Heuristic variations for terms ending in .js / js or with dashes
    if normalized.endswith(".js"):
        aliases.add(normalized[:-3] + "js")
        aliases.add(normalized[:-3])
    elif normalized.endswith("js") and len(normalized) > 3:
        aliases.add(normalized[:-2] + ".js")
        aliases.add(normalized[:-2])

    if "-" in normalized:
        aliases.add(normalized.replace("-", " "))
        aliases.add(normalized.replace("-", ""))
    elif " " in normalized:
        aliases.add(normalized.replace(" ", "-"))

    return aliases

