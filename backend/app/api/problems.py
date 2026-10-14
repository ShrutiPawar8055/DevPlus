from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories import ProblemRepository
from ..schemas import ProblemListOut, ProblemOut

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=list[ProblemListOut])
def list_problems(db: Session = Depends(get_db)):
    """Return all available LLD practice problems."""
    repo = ProblemRepository(db)
    problems = repo.get_all()
    return [ProblemListOut.model_validate(p) for p in problems]


@router.get("/{problem_id}", response_model=ProblemOut)
def get_problem(problem_id: int, db: Session = Depends(get_db)):
    """Return a single problem with its full details."""
    repo = ProblemRepository(db)
    problem = repo.get_by_id(problem_id)
    if problem is None:
        raise HTTPException(status_code=404, detail="Problem not found")
    return ProblemRepository.to_problem_out(problem)
