import re

from ...schemas import CategoryScore, Feedback, ProblemOut
from .base import FeedbackEvaluator


class RuleBasedFeedbackEvaluator(FeedbackEvaluator):
    """Deterministic evaluator that scores a solution using heuristics.

    This is the fallback used when no LLM API key is configured. It checks
    measurable signals: requirement coverage, presence of classes/interfaces,
    SOLID-related vocabulary, and relationship description.

    Every check here is intentionally transparent and reproducible — a learner
    can read the code and understand exactly why they got the score they did.
    """

    # Keywords that indicate good LLD practices
    SOLID_KEYWORDS = [
        "single responsibility", "open/closed", "open closed", "liskov",
        "interface segregation", "dependency inversion", "dependency injection",
        "solid", "encapsulation", "abstraction", "polymorphism", "inheritance",
    ]
    RELATIONSHIP_KEYWORDS = [
        "extends", "implements", "composition", "aggregation", "association",
        "uses", "has-a", "has a", "is-a", "is a", "dependency", "delegates",
    ]
    ABSTRACTION_KEYWORDS = [
        "interface", "abstract", "protocol", "contract", "base class",
    ]

    def evaluate(
        self,
        problem: ProblemOut,
        solution_text: str,
        solution_code: str,
    ) -> Feedback:
        combined = (solution_text + "\n" + solution_code).lower()

        category_scores = [
            self._score_requirement_coverage(problem, combined),
            self._score_responsibility_assignment(combined, solution_code),
            self._score_abstraction(combined, solution_code),
            self._score_solid_principles(combined),
            self._score_relationships(combined),
        ]

        overall = sum(c.score for c in category_scores) / len(category_scores)
        overall = round(overall, 1)

        strengths = self._collect_strengths(category_scores)
        improvements = self._collect_improvements(category_scores)

        summary = self._build_summary(overall, strengths, improvements)

        return Feedback(
            overall_score=overall,
            summary=summary,
            strengths=strengths,
            improvements=improvements,
            category_scores=category_scores,
            approach="rule_based",
        )

    # ---- Per-category scoring -------------------------------------------------

    def _score_requirement_coverage(self, problem: ProblemOut, text: str) -> CategoryScore:
        """Score how many of the problem's requirements are addressed."""
        if not problem.requirements:
            return CategoryScore(
                category="Requirement Coverage", score=7.0,
                comment="No explicit requirements were provided for this problem.",
            )

        keywords = self._extract_requirement_keywords(problem.requirements)
        if not keywords:
            return CategoryScore(
                category="Requirement Coverage", score=7.0,
                comment="Could not extract keywords from the requirements.",
            )

        hits = sum(1 for kw in keywords if kw in text)
        ratio = hits / len(keywords)
        score = round(ratio * 10, 1)

        comment = (
            f"Addressed {hits} of {len(keywords)} key requirement topics."
            if score >= 5
            else f"Only {hits} of {len(keywords)} key requirement topics appear in your solution. "
                 f"Make sure you explicitly cover each requirement."
        )
        return CategoryScore(category="Requirement Coverage", score=score, comment=comment)

    def _score_responsibility_assignment(self, text: str, code: str) -> CategoryScore:
        """Score whether the solution defines multiple distinct responsibilities."""
        class_count = len(re.findall(r"\b(class|interface)\s+\w+", code, re.IGNORECASE))
        # Also count responsibilities mentioned in prose
        responsibility_mentions = len(re.findall(
            r"\b(responsible for|handles|manages|owns|coordinates|controller|manager|service|repository)\b",
            text, re.IGNORECASE,
        ))

        score = min(10.0, 2.0 + class_count * 1.5 + responsibility_mentions * 0.5)
        score = round(score, 1)

        if class_count >= 4:
            comment = f"Good — you defined {class_count} classes/interfaces showing clear responsibility split."
        elif class_count >= 2:
            comment = f"You defined {class_count} classes. Consider splitting further so each class has one clear responsibility."
        else:
            comment = "Define multiple classes, each with a single, well-named responsibility. A single god-class is a common LLD smell."

        return CategoryScore(category="Responsibility Assignment", score=score, comment=comment)

    def _score_abstraction(self, text: str, code: str) -> CategoryScore:
        """Score whether the solution uses interfaces or abstractions."""
        has_interface = bool(re.search(r"\b(interface|abstract|protocol)\b", text + "\n" + code, re.IGNORECASE))
        has_interface_decl = bool(re.search(r"\b(interface|abstract\s+class)\b", code, re.IGNORECASE))

        score = 4.0
        if has_interface:
            score += 3.0
        if has_interface_decl:
            score += 3.0
        score = round(min(10.0, score), 1)

        comment = (
            "Good use of interfaces/abstractions to decouple implementations."
            if score >= 7
            else "Introduce interfaces or abstract classes so high-level modules depend on abstractions, not concrete classes."
        )
        return CategoryScore(category="Abstraction", score=score, comment=comment)

    def _score_solid_principles(self, text: str) -> CategoryScore:
        """Score whether the solution references SOLID-related concepts."""
        hits = sum(1 for kw in self.SOLID_KEYWORDS if kw in text)
        score = round(min(10.0, hits * 1.8), 1)

        if hits >= 4:
            comment = "Strong awareness of SOLID principles in your design reasoning."
        elif hits >= 1:
            comment = "You mention some good principles. Explicitly tie each principle to a specific class or decision in your design."
        else:
            comment = "No SOLID principles mentioned. Review each class against Single Responsibility, Open/Closed, and Dependency Inversion."

        return CategoryScore(category="SOLID Principles", score=score, comment=comment)

    def _score_relationships(self, text: str) -> CategoryScore:
        """Score whether relationships between classes are described."""
        hits = sum(1 for kw in self.RELATIONSHIP_KEYWORDS if kw in text)
        score = round(min(10.0, 2.0 + hits * 1.3), 1)

        if hits >= 3:
            comment = "Relationships between classes are well described."
        else:
            comment = "Describe how classes relate: which extends/implements which, which uses which, and where composition is used."

        return CategoryScore(category="Relationships", score=score, comment=comment)

    # ---- Helpers --------------------------------------------------------------

    @staticmethod
    def _extract_requirement_keywords(requirements: list[str]) -> list[str]:
        """Pull the most meaningful words from each requirement line."""
        keywords: list[str] = []
        stop_words = {"the", "a", "an", "and", "or", "to", "of", "for", "in", "on",
                      "with", "should", "must", "be", "is", "are", "was", "were",
                      "it", "its", "this", "that", "these", "those", "from", "by"}
        for req in requirements:
            words = re.findall(r"\b[a-zA-Z]{4,}\b", req.lower())
            for w in words:
                if w not in stop_words and w not in keywords:
                    keywords.append(w)
        return keywords[:20]

    def _collect_strengths(self, scores: list[CategoryScore]) -> list[str]:
        """Return comments for categories that scored well (>= 7)."""
        return [
            f"{s.category}: {s.comment}"
            for s in scores if s.score >= 7
        ] or ["Your solution has a clear structure that can be built upon."]

    def _collect_improvements(self, scores: list[CategoryScore]) -> list[str]:
        """Return comments for categories that scored poorly (< 7)."""
        return [
            f"{s.category}: {s.comment}"
            for s in scores if s.score < 7
        ] or ["All categories scored well. Try adding more detail on trade-offs you considered."]

    @staticmethod
    def _build_summary(overall: float, strengths: list[str], improvements: list[str]) -> str:
        tone = "solid" if overall >= 7 else "promising but needs work" if overall >= 4 else "needs significant work"
        return (
            f"Overall score {overall}/10. This is a {tone} attempt. "
            f"You have {len(strengths)} strength(s) and {len(improvements)} area(s) to improve. "
            "Review the category feedback below, then try again with the suggested changes."
        )
