from __future__ import annotations

import re
from collections import Counter

TOKEN_RE = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def deterministic_similarity(query: str, content: str, tags: list[str]) -> float:
    """Small deterministic scorer used instead of external embeddings.

    It is intentionally simple for public review: token overlap gives a stable
    semantic-ish baseline, while tags model precomputed semantic labels.
    """
    query_terms = Counter(tokenize(query))
    if not query_terms:
        return 0.0
    content_terms = Counter(tokenize(content))
    tag_terms = Counter(tokenize(" ".join(tags)))
    overlap = sum(min(count, content_terms.get(term, 0)) for term, count in query_terms.items())
    tag_overlap = sum(min(count, tag_terms.get(term, 0)) for term, count in query_terms.items())
    normalized = overlap / max(1, len(query_terms))
    tag_bonus = 0.5 * tag_overlap / max(1, len(query_terms))
    return round(normalized + tag_bonus, 4)


def matched_tags(query: str, tags: list[str]) -> list[str]:
    q = set(tokenize(query))
    return [tag for tag in tags if q.intersection(tokenize(tag))]
