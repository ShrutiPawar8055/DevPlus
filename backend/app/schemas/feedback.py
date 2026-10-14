from pydantic import BaseModel


class CategoryScore(BaseModel):
    """Score and comment for a single evaluation category."""

    category: str
    score: float  # 0-10
    comment: str


class Feedback(BaseModel):
    """Structured feedback produced by an evaluator for an attempt."""

    overall_score: float  # 0-10
    summary: str
    strengths: list[str]
    improvements: list[str]
    category_scores: list[CategoryScore]
    approach: str  # "llm" or "rule_based"
