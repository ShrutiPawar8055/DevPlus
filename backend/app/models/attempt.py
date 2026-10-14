from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from ..database import Base


class Attempt(Base):
    """A learner's submission for a problem, including the produced feedback.

    The feedback is stored as a JSON string so it can evolve without schema
    migrations. The `status` field captures the lifecycle: pending -> evaluating
    -> completed (or failed).
    """

    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    problem_id = Column(Integer, ForeignKey("problems.id"), nullable=False)
    solution_text = Column(Text, nullable=False)  # prose description of the design
    solution_code = Column(Text, default="")  # code snippets (classes/interfaces)
    status = Column(String(20), nullable=False, default="pending")
    # pending | evaluating | completed | failed
    overall_score = Column(Float, nullable=True)  # 0-10
    feedback = Column(Text, nullable=True)  # JSON-serialised Feedback object
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    problem = relationship("Problem")
