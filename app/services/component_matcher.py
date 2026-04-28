from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import Iterable

from app.schemas.components import (
    CatalogComponent,
    ComponentMatch,
    ExtractedComponent,
    MatchedComponent,
)

_NON_ALNUM = re.compile(r"[^a-z0-9]+")


def _normalize(s: str) -> str:
    return _NON_ALNUM.sub("", s.lower())


def _tokens(s: str) -> set[str]:
    # Split CamelCase, snake_case, kebab-case, spaces
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", s)
    spaced = re.sub(r"[_\-/]+", " ", spaced)
    return {t.lower() for t in spaced.split() if t}


def _name_score(figma_name: str, candidate: str) -> float:
    a, b = _normalize(figma_name), _normalize(candidate)
    if not a or not b:
        return 0.0
    if a == b:
        return 1.0
    ta, tb = _tokens(figma_name), _tokens(candidate)
    # All candidate tokens present as tokens in figma name -> strong signal
    if ta and tb and tb.issubset(ta):
        ratio = len(tb) / len(ta)
        return 0.7 + 0.2 * ratio  # 0.7..0.9
    seq = SequenceMatcher(None, a, b).ratio()
    if not ta or not tb:
        return min(seq, 0.55)
    shared = ta & tb
    jaccard = len(shared) / len(ta | tb)
    if not shared:
        # no shared token -> heavily dampen char-level similarity to avoid false positives
        return min(seq * 0.6, 0.55)
    # at least one shared token: prefer jaccard, complemented by seq
    return max(jaccard, seq * 0.7)


def _score_against_catalog_entry(
    extracted: ExtractedComponent,
    entry: CatalogComponent,
) -> ComponentMatch | None:
    figma_name = extracted.figma_name.split(",")[0].split("=")[0].strip() or extracted.figma_name
    # Tags are generic and produce false positives; weight them down heavily.
    candidates: list[tuple[str, str, float]] = [(entry.name, "name", 1.0)]
    candidates += [(a, "alias", 1.0) for a in entry.aliases]
    candidates += [(t, "tag", 0.4) for t in entry.tags]

    best: tuple[float, str, str] | None = None
    for value, kind, weight in candidates:
        if kind in ("name", "alias") and _normalize(value) == _normalize(figma_name):
            return ComponentMatch(
                dmbui_name=entry.name,
                confidence=1.0,
                reason=f"exact {kind} match on '{value}'",
            )
        score = _name_score(figma_name, value) * weight
        if best is None or score > best[0]:
            best = (score, value, kind)

    if best is None:
        return None

    score, value, kind = best
    return ComponentMatch(
        dmbui_name=entry.name,
        confidence=round(score, 3),
        reason=f"fuzzy match on {kind} '{value}'",
    )


def match_components(
    extracted_list: Iterable[ExtractedComponent],
    catalog_entries: list[CatalogComponent],
    threshold: float = 0.6,
    top_k_suggestions: int = 3,
) -> list[MatchedComponent]:
    results: list[MatchedComponent] = []
    for extracted in extracted_list:
        scored: list[ComponentMatch] = []
        for entry in catalog_entries:
            m = _score_against_catalog_entry(extracted, entry)
            if m is not None:
                scored.append(m)

        scored.sort(key=lambda x: x.confidence, reverse=True)
        best = scored[0] if scored else None
        matched = bool(best and best.confidence >= threshold)
        suggestions = [s for s in scored[:top_k_suggestions] if not matched or s is not best]

        results.append(
            MatchedComponent(
                extracted=extracted,
                best_match=best if matched else None,
                suggestions=suggestions if not matched else [],
                matched=matched,
            )
        )
    return results




