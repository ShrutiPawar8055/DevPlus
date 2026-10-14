from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from ..database import Base


class Problem(Base):
    """A Low-Level Design practice problem.

    Stores the problem statement, requirements, hints, and the evaluation
    criteria that the feedback engine will use to assess a learner's solution.
    """

    __tablename__ = "problems"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    difficulty = Column(String(20), nullable=False)  # easy, medium, hard
    short_description = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text, nullable=False)  # newline-separated list
    hints = Column(Text, default="")  # newline-separated list, optional
    evaluation_criteria = Column(Text, nullable=False)  # newline-separated list
    created_at = Column(DateTime(timezone=True), server_default=func.now())
