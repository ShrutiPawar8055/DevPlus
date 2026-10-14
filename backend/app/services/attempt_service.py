from typing import Optional

from sqlalchemy.orm import Session

from ..models import Attempt
from ..repositories import AttemptRepository, ProblemRepository
from ..schemas import AttemptCreate, AttemptOut, AttemptSummaryOut
from .evaluator import evaluate_with_fallback


class AttemptService:
    """Orchestrates the attempt lifecycle: create, evaluate, retrieve.

    The service coordinates the repositories and the evaluator. It is the
    single entry point for the API layer, keeping HTTP concerns out of the
    domain logic.
    """

    def __init__(self, db: Session):
        self.problem_repo = ProblemRepository(db)
        self.attempt_repo = AttemptRepository(db)

    def create_attempt(self, problem_id: int, data: AttemptCreate) -> AttemptOut:
        """Create a new attempt and evaluate it, returning the full result.

        Evaluation happens synchronously here (LLM or rule-based with fallback).
        For an MVP this is acceptable; for higher load this could move to a
        background job with the attempt starting in 'evaluating' status.
        """
        problem = self.problem_repo.get_by_id(problem_id)
        if problem is None:
            raise ValueError(f"Problem with id {problem_id} not found.")

        attempt = self.attempt_repo.create(problem_id, data)
        self.attempt_repo.update_status(attempt, "evaluating")

        problem_out = ProblemRepository.to_problem_out(problem)

        try:
            feedback = evaluate_with_fallback(
                problem_out,
                attempt.solution_text,
                attempt.solution_code,
            )
            attempt = self.attempt_repo.save_feedback(attempt, feedback)
        except Exception as exc:  # pragma: no cover - defensive
            attempt = self.attempt_repo.mark_failed(attempt, str(exc))

        return self._to_attempt_out(attempt)

    def get_attempt(self, attempt_id: int) -> Optional[AttemptOut]:
        """Return a single attempt with its feedback, or None if not found."""
        attempt = self.attempt_repo.get_by_id(attempt_id)
        if attempt is None:
            return None
        return self._to_attempt_out(attempt)

    def get_history(self, problem_id: int) -> list[AttemptSummaryOut]:
        """Return the attempt history for a problem (newest first)."""
        attempts = self.attempt_repo.get_by_problem(problem_id)
        return [
            AttemptSummaryOut(
                id=a.id,
                problem_id=a.problem_id,
                status=a.status,
                overall_score=a.overall_score,
                created_at=a.created_at,
            )
            for a in attempts
        ]

    # ---- Mapping helpers ------------------------------------------------------

    def _to_attempt_out(self, attempt: Attempt) -> AttemptOut:
        feedback = AttemptRepository.parse_feedback(attempt)
        return AttemptOut(
            id=attempt.id,
            problem_id=attempt.problem_id,
            solution_text=attempt.solution_text,
            solution_code=attempt.solution_code,
            status=attempt.status,
            overall_score=attempt.overall_score,
            feedback=feedback,
            error_message=attempt.error_message,
            created_at=attempt.created_at,
        )
