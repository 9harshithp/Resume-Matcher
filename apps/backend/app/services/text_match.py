"""Whole-term keyword matching shared by scoring, tailoring and refinement."""

import re
from typing import Optional

from app.services.skill_aliases import get_skill_aliases

# Han (including supplementary planes), Kana, and Hangul syllables/Jamo.
_CJK_CHAR_CLASS = (
    r"[ᄀ-ᇿ぀-ヿ㄰-㆏ㇰ-ㇿ"
    r"㐀-鿿ꥠ-꥿가-퟿豈-﫿"
    r"ｦ-ￜ\U0001b000-\U0001b16f\U00020000-\U0003ffff]"
)
_CJK_RE = re.compile(_CJK_CHAR_CLASS)


def keyword_in_text(keyword: str, text: str, allow_aliases: bool = False) -> bool:
    """Check for a CJK substring or a bounded non-CJK term in text.

    Han, Kana, and Hangul characters may adjoin Latin skills without whitespace,
    so they also form boundaries for adjacent Latin terms. Other word characters
    retain boundaries so 'python' does not match 'pythonic' and 'java' does not
    match 'javascript'.

    When `allow_aliases=True`, also returns True if any canonical alias or synonym
    of the keyword (e.g. 'k8s' for 'kubernetes') matches the text.
    """
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return False
    normalized_text = text.lower()

    if _match_single_term(normalized_keyword, normalized_text):
        return True

    if allow_aliases:
        for alias in get_skill_aliases(normalized_keyword):
            if alias != normalized_keyword and _match_single_term(alias, normalized_text):
                return True

    return False


def find_matching_alias(keyword: str, text: str) -> Optional[str]:
    """Return the exact alias that matched in text, or None if no match."""
    normalized_keyword = keyword.strip().lower()
    if not normalized_keyword:
        return None
    normalized_text = text.lower()

    if _match_single_term(normalized_keyword, normalized_text):
        return normalized_keyword

    for alias in get_skill_aliases(normalized_keyword):
        if _match_single_term(alias, normalized_text):
            return alias

    return None


def _match_single_term(term: str, normalized_text: str) -> bool:
    """Check whole-word match for a single term in normalized text."""
    if _CJK_RE.search(term):
        return term in normalized_text
    escaped = re.escape(term)
    pattern = (
        rf"(?:(?<!\w)|(?<={_CJK_CHAR_CLASS}))"
        rf"{escaped}"
        rf"(?:(?!\w)|(?={_CJK_CHAR_CLASS}))"
    )
    return bool(re.search(pattern, normalized_text))


def normalize_skill_key(skill: str) -> str:
    """Normalize a skill for case-insensitive comparisons."""
    return re.sub(r"\s+", " ", skill.strip()).casefold()
