import json
from typing import Optional

from sqlalchemy.orm import Session

from ..models import Attempt
from ..schemas import AttemptCreate, Feedback


class AttemptRepository:
    """Data access for learner attempts."""

    def __init__(self, db: Session):
        self.db = db

    def create(self, problem_id: int, data: AttemptCreate) -> Attempt:
        """Create and persist a new attempt with 'pending' status."""
        attempt = Attempt(
            problem_id=problem_id,
            solution_text=data.solution_text,
            solution_code=data.solution_code,
            status="pending",
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_by_id(self, attempt_id: int) -> Optional[Attempt]:
        """Return an attempt by its id, or None if not found."""
        return self.db.query(Attempt).filter(Attempt.id == attempt_id).first()

    def get_by_problem(self, problem_id: int) -> list[Attempt]:
        """Return all attempts for a problem, newest first (id breaks ties)."""
        return (
            self.db.query(Attempt)
            .filter(Attempt.problem_id == problem_id)
            .order_by(Attempt.created_at.desc(), Attempt.id.desc())
            .all()
        )

    def update_status(self, attempt: Attempt, status: str) -> Attempt:
        """Update the status of an attempt."""
        attempt.status = status
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def save_feedback(self, attempt: Attempt, feedback: Feedback) -> Attempt:
        """Persist structured feedback and mark the attempt as completed."""
        attempt.feedback = feedback.model_dump_json()
        attempt.overall_score = feedback.overall_score
        attempt.status = "completed"
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def mark_failed(self, attempt: Attempt, error_message: str) -> Attempt:
        """Mark an attempt as failed and store the error message."""
        attempt.status = "failed"
        attempt.error_message = error_message
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    @staticmethod
    def parse_feedback(attempt: Attempt) -> Optional[Feedback]:
        """Parse the JSON feedback string into a Feedback object, or None."""
        if not attempt.feedback:
            return None
        try:
            return Feedback(**json.loads(attempt.feedback))
        except (json.JSONDecodeError, ValueError):
            return None
