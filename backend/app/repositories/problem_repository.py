from typing import Optional

from sqlalchemy.orm import Session

from ..models import Problem


def _split_lines(text: str) -> list[str]:
    """Split a newline-separated text field into a clean list of strings."""
    return [line.strip() for line in (text or "").splitlines() if line.strip()]


class ProblemRepository:
    """Data access for LLD practice problems."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Problem]:
        """Return all problems ordered by id."""
        return self.db.query(Problem).order_by(Problem.id).all()

    def get_by_id(self, problem_id: int) -> Optional[Problem]:
        """Return a single problem by its id, or None if not found."""
        return self.db.query(Problem).filter(Problem.id == problem_id).first()

    def get_by_slug(self, slug: str) -> Optional[Problem]:
        """Return a single problem by its slug, or None if not found."""
        return self.db.query(Problem).filter(Problem.slug == slug).first()

    def create(self, problem: Problem) -> Problem:
        """Persist a new problem to the database."""
        self.db.add(problem)
        self.db.commit()
        self.db.refresh(problem)
        return problem

    @staticmethod
    def to_problem_out(problem: Problem):
        """Convert a Problem ORM object to the ProblemOut schema (with split lists)."""
        from ..schemas import ProblemOut

        return ProblemOut(
            id=problem.id,
            title=problem.title,
            slug=problem.slug,
            difficulty=problem.difficulty,
            short_description=problem.short_description,
            description=problem.description,
            requirements=_split_lines(problem.requirements),
            hints=_split_lines(problem.hints),
            evaluation_criteria=_split_lines(problem.evaluation_criteria),
        )
