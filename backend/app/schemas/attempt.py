from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .feedback import Feedback


class AttemptCreate(BaseModel):
    """Payload submitted by a learner for a new attempt."""

    solution_text: str
    solution_code: str = ""


class AttemptSummaryOut(BaseModel):
    """Lightweight attempt view used in the history list."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    problem_id: int
    status: str
    overall_score: Optional[float]
    created_at: datetime


class AttemptOut(AttemptSummaryOut):
    """Full attempt view including the solution and structured feedback."""

    solution_text: str
    solution_code: str
    feedback: Optional[Feedback] = None
    error_message: Optional[str] = None
