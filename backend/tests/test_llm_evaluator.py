"""Tests for the LLM evaluator's response parsing (no network calls)."""

import pytest

from app.services.evaluator import LLMFeedbackEvaluator
from app.schemas import Feedback


def test_parse_valid_json():
    """A clean JSON response should parse into a Feedback object."""
    raw = """{
        "overall_score": 7.5,
        "summary": "Good attempt.",
        "strengths": ["Clear classes"],
        "improvements": ["Add interfaces"],
        "category_scores": [
            {"category": "Abstraction", "score": 8.0, "comment": "Good"}
        ]
    }"""
    feedback = LLMFeedbackEvaluator._parse_feedback(raw)
    assert isinstance(feedback, Feedback)
    assert feedback.overall_score == 7.5
    assert feedback.approach == "llm"
    assert feedback.strengths == ["Clear classes"]
    assert len(feedback.category_scores) == 1
    assert feedback.category_scores[0].category == "Abstraction"


def test_parse_json_with_code_fences():
    """JSON wrapped in markdown code fences should still parse."""
    raw = "```json\n{\"overall_score\": 6.0, \"summary\": \"ok\", \"strengths\": [], \"improvements\": [], \"category_scores\": []}\n```"
    feedback = LLMFeedbackEvaluator._parse_feedback(raw)
    assert feedback.overall_score == 6.0


def test_parse_json_with_surrounding_text():
    """JSON embedded in prose should be extracted defensively."""
    raw = "Here is your feedback:\n{\"overall_score\": 5.0, \"summary\": \"mid\", \"strengths\": [], \"improvements\": [], \"category_scores\": []}\nHope that helps!"
    feedback = LLMFeedbackEvaluator._parse_feedback(raw)
    assert feedback.overall_score == 5.0


def test_parse_invalid_json_raises():
    """Non-JSON responses should raise a ValueError."""
    with pytest.raises(ValueError):
        LLMFeedbackEvaluator._parse_feedback("This is not JSON at all")


def test_evaluate_without_api_key_raises():
    """Calling evaluate with no API key should raise RuntimeError."""
    evaluator = LLMFeedbackEvaluator(api_key="", base_url="http://localhost")
    with pytest.raises(RuntimeError):
        from app.schemas import ProblemOut
        evaluator.evaluate(
            ProblemOut(
                id=1, title="t", slug="t", difficulty="easy",
                short_description="d", description="d",
                requirements=[], hints=[], evaluation_criteria=[],
            ),
            solution_text="x",
            solution_code="",
        )
