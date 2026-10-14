from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import AttemptCreate, AttemptOut, AttemptSummaryOut
from ..services import AttemptService

router = APIRouter(tags=["attempts"])


@router.post("/api/problems/{problem_id}/attempts", response_model=AttemptOut)
def create_attempt(
    problem_id: int,
    data: AttemptCreate,
    db: Session = Depends(get_db),
):
    """Submit a solution for a problem and receive evaluated feedback."""
    service = AttemptService(db)
    try:
        return service.create_attempt(problem_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.get(
    "/api/problems/{problem_id}/attempts",
    response_model=list[AttemptSummaryOut],
)
def list_attempts(problem_id: int, db: Session = Depends(get_db)):
    """Return the attempt history for a problem (newest first)."""
    service = AttemptService(db)
    return service.get_history(problem_id)


@router.get("/api/attempts/{attempt_id}", response_model=AttemptOut)
def get_attempt(attempt_id: int, db: Session = Depends(get_db)):
    """Return a single attempt with its feedback."""
    service = AttemptService(db)
    attempt = service.get_attempt(attempt_id)
    if attempt is None:
        raise HTTPException(status_code=404, detail="Attempt not found")
    return attempt
