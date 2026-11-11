"""Tests for the upgraded ATS Matching Engine with canonical skill aliases."""

from typing import Any
import pytest

from app.services.ats import _compute_skills_coverage, compute_ats_score
from app.services.refiner import calculate_keyword_match, analyze_keyword_gaps
from app.services.skill_aliases import get_skill_aliases, normalize_term
from app.services.text_match import keyword_in_text, find_matching_alias


class TestSkillAliases:
    def test_canonical_aliases_lookup(self) -> None:
        k8s_aliases = get_skill_aliases("Kubernetes")
        assert "k8s" in k8s_aliases
        assert "kubernetes" in k8s_aliases

        aws_aliases = get_skill_aliases("AWS")
        assert "amazon web services" in aws_aliases
        assert "aws" in aws_aliases

        postgres_aliases = get_skill_aliases("PostgreSQL")
        assert "postgres" in postgres_aliases
        assert "postgresql" in postgres_aliases

        go_aliases = get_skill_aliases("Golang")
        assert "go" in go_aliases
        assert "golang" in go_aliases

        ts_aliases = get_skill_aliases("TypeScript")
        assert "ts" in ts_aliases
        assert "typescript" in ts_aliases

    def test_heuristic_variations(self) -> None:
        # nodejs <-> node.js
        node_aliases = get_skill_aliases("node.js")
        assert "nodejs" in node_aliases

        # full-stack <-> full stack
        fs_aliases = get_skill_aliases("full-stack")
        assert "full stack" in fs_aliases or "fullstack" in fs_aliases


class TestKeywordInTextWithAliases:
    def test_alias_matching(self) -> None:
        text = "Engineered distributed systems using k8s, postgres, and aws."
        
        # Exact word is not present, but alias is:
        assert not keyword_in_text("Kubernetes", text, allow_aliases=False)
        assert keyword_in_text("Kubernetes", text, allow_aliases=True)

        assert not keyword_in_text("PostgreSQL", text, allow_aliases=False)
        assert keyword_in_text("PostgreSQL", text, allow_aliases=True)

        assert not keyword_in_text("Amazon Web Services", text, allow_aliases=False)
        assert keyword_in_text("Amazon Web Services", text, allow_aliases=True)

    def test_word_boundaries_preserved_with_aliases(self) -> None:
        text = "I am going to Google."
        # 'Go' alias should NOT match 'going' or 'Google'
        assert not keyword_in_text("Go", text, allow_aliases=True)
        assert not keyword_in_text("Golang", text, allow_aliases=True)

        # 'Java' should not match 'JavaScript'
        js_text = "Proficient in JavaScript and React."
        assert not keyword_in_text("Java", js_text, allow_aliases=True)

    def test_find_matching_alias(self) -> None:
        text = "Architected real-time streaming with k8s."
        matched = find_matching_alias("Kubernetes", text)
        assert matched == "k8s"


class TestAtsScoreWithAliases:
    def test_skills_coverage_with_aliases(self) -> None:
        resume = {
            "additional": {
                "technicalSkills": ["K8s", "Postgres", "AWS", "TS"]
            }
        }
        job_keywords = {
            "required_skills": ["Kubernetes", "PostgreSQL", "Amazon Web Services", "TypeScript"],
            "preferred_skills": []
        }
        score = _compute_skills_coverage(resume, job_keywords, allow_aliases=True)
        assert score == 100.0

    def test_calculate_keyword_match_with_aliases(self) -> None:
        resume = {
            "summary": "Built cloud solutions using k8s and deployed to aws with postgres."
        }
        job_keywords = {
            "required_skills": ["Kubernetes", "Amazon Web Services"],
            "preferred_skills": ["PostgreSQL"],
            "keywords": []
        }
        match_pct = calculate_keyword_match(resume, job_keywords, allow_aliases=True)
        assert match_pct == 100.0

    def test_analyze_keyword_gaps_with_aliases(self) -> None:
        master = {
            "summary": "Extensive experience maintaining k8s clusters in production."
        }
        tailored = {
            "summary": "Software engineer with general cloud experience."
        }
        jd_keywords = {
            "required_skills": ["Kubernetes"],
            "preferred_skills": [],
            "keywords": []
        }
        gaps = analyze_keyword_gaps(jd_keywords, tailored, master, allow_aliases=True)
        # Kubernetes was not in tailored, but k8s was in master -> recognized as injectable!
        assert "Kubernetes" in gaps.injectable_keywords
        assert "Kubernetes" not in gaps.non_injectable_keywords

    def test_compute_ats_score_reports_alias_matches(self) -> None:
        resume = {
            "personalInfo": {"name": "Alex", "title": "DevOps Engineer", "email": "a@b.com"},
            "summary": "Deployed microservices to k8s on aws.",
            "workExperience": [
                {"title": "DevOps Engineer", "company": "Cloud Corp", "years": "Jan 2021 - Present"}
            ],
            "education": [
                {"degree": "BS CS", "institution": "Tech Uni", "years": "2016 - 2020"}
            ],
            "additional": {
                "technicalSkills": ["k8s", "aws"]
            }
        }
        job_keywords = {
            "role": "DevOps Engineer",
            "required_skills": ["Kubernetes", "Amazon Web Services"],
            "preferred_skills": [],
            "keywords": []
        }
        ats_result = compute_ats_score(
            refined_resume=resume,
            job_keywords=job_keywords,
            keyword_match_percentage=100.0,
            missing_keywords=[],
            injectable_keywords=[],
        )
        assert ats_result["overall_score"] > 80.0
        assert "alias_matches" in ats_result
        alias_keywords = [m["keyword"] for m in ats_result["alias_matches"]]
        assert "Kubernetes" in alias_keywords
        assert "Amazon Web Services" in alias_keywords
        assert any("Equivalents recognized" in rec or "Skills recognized" in rec for rec in ats_result["recommendations"])

