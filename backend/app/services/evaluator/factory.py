from ...config import settings
from ...schemas import Feedback, ProblemOut
from .base import FeedbackEvaluator
from .llm_evaluator import LLMFeedbackEvaluator
from .rule_based_evaluator import RuleBasedFeedbackEvaluator


def get_evaluator() -> FeedbackEvaluator:
    """Return the best available evaluator.

    If an LLM API key is configured, the LLM evaluator is used. Otherwise the
    deterministic rule-based evaluator is returned. This is the single point
    where the evaluation strategy is decided.
    """
    if settings.llm_enabled:
        return LLMFeedbackEvaluator()
    return RuleBasedFeedbackEvaluator()


def evaluate_with_fallback(
    problem: ProblemOut,
    solution_text: str,
    solution_code: str,
) -> Feedback:
    """Evaluate using the LLM if available, falling back to rule-based on failure.

    This guarantees the learner always receives feedback even if the LLM API
    is slow, misconfigured, or returns unparseable output.
    """
    evaluator = get_evaluator()

    if isinstance(evaluator, LLMFeedbackEvaluator):
        try:
            return evaluator.evaluate(problem, solution_text, solution_code)
        except Exception:
            # LLM failed for any reason — fall back to deterministic evaluation
            # so the learner is never left without feedback.
            pass

    return RuleBasedFeedbackEvaluator().evaluate(problem, solution_text, solution_code)
