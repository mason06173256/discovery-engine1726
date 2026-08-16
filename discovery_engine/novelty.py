from __future__ import annotations

from typing import List

from .models import Hypothesis, Source


class NoveltyEvaluator:
    """Lightweight evaluator that classifies novelty without claiming proof of originality."""

    @staticmethod
    def evaluate_hypothesis(hypothesis: Hypothesis, sources: List[Source]) -> str:
        if not hypothesis.description:
            return "unable_to_determine"

        if not sources:
            return "apparently_novel"

        if any(source.source_id in hypothesis.supporting_sources for source in sources):
            return "modification"

        return "probably_known"

    @staticmethod
    def critique_hypothesis(hypothesis: Hypothesis) -> List[str]:
        notes: List[str] = []
        if not hypothesis.supporting_sources:
            notes.append("The hypothesis lacks retrieved evidence support.")
        if hypothesis.confidence < 0.4:
            notes.append("The confidence score is low and the claim remains tentative.")
        if hypothesis.novelty_status in {"known", "probably_known"}:
            notes.append("The idea is likely already established or only a refinement of known work.")
        if not notes:
            notes.append("The hypothesis remains tentative until more retrieved evidence, testing, or critique is added.")
        return notes
