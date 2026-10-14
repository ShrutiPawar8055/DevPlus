from pydantic import BaseModel, ConfigDict


class ProblemListOut(BaseModel):
    """Summary of a problem used in the problem list view."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    difficulty: str
    short_description: str


class ProblemOut(ProblemListOut):
    """Full problem details including requirements, hints and criteria."""

    description: str
    requirements: list[str]
    hints: list[str]
    evaluation_criteria: list[str]
