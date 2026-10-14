"""Tests for the rule-based feedback evaluator."""

import pytest

from app.schemas import ProblemOut
from app.services.evaluator import RuleBasedFeedbackEvaluator


def make_problem() -> ProblemOut:
    return ProblemOut(
        id=1,
        title="Design a Parking Lot",
        slug="parking-lot",
        difficulty="medium",
        short_description="A parking lot system.",
        description="Design a parking lot.",
        requirements=[
            "Support vehicle types: motorcycle, car, truck",
            "Each floor has spots of different sizes",
            "Issue a ticket on entry",
        ],
        hints=[],
        evaluation_criteria=["Clear separation of responsibilities"],
    )


def test_evaluator_returns_feedback_structure():
    """A valid solution must produce a complete Feedback object."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    feedback = evaluator.evaluate(
        problem,
        solution_text=(
            "I use a Vehicle abstract class with Car and Truck subclasses. "
            "Spot is an interface. ParkingLot has many floors via composition. "
            "Ticket is responsible for entry time. PricingStrategy uses dependency injection. "
            "Each class follows single responsibility. Floors extend nothing but use spots. "
            "I follow open closed principle and liskov substitution."
        ),
        solution_code=(
            "abstract class Vehicle {}\n"
            "class Car extends Vehicle {}\n"
            "interface Spot {}\n"
            "class Floor {}\n"
            "class ParkingLot {}\n"
            "class Ticket {}\n"
            "interface PricingStrategy {}"
        ),
    )

    assert 0 <= feedback.overall_score <= 10
    assert feedback.approach == "rule_based"
    assert len(feedback.category_scores) == 5
    assert isinstance(feedback.strengths, list)
    assert isinstance(feedback.improvements, list)
    assert feedback.summary


def test_evaluator_scores_low_for_minimal_solution():
    """A solution with no classes and little text should score poorly."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    feedback = evaluator.evaluate(problem, solution_text="I made a parking lot.", solution_code="")

    assert feedback.overall_score < 5
    # Responsibility assignment should be low with no classes defined
    resp_score = next(s for s in feedback.category_scores if s.category == "Responsibility Assignment")
    assert resp_score.score < 5


def test_evaluator_rewards_multiple_classes():
    """Defining many distinct classes should raise the responsibility score."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    code = "\n".join(f"class Class{i} {{}}" for i in range(6))
    feedback = evaluator.evaluate(problem, solution_text="design", solution_code=code)

    resp_score = next(s for s in feedback.category_scores if s.category == "Responsibility Assignment")
    assert resp_score.score >= 7


def test_evaluator_rewards_interfaces():
    """Using interface/abstract keywords should raise the abstraction score."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    feedback = evaluator.evaluate(
        problem,
        solution_text="I define an interface and an abstract class.",
        solution_code="interface Spot {}\nabstract class Vehicle {}",
    )

    abs_score = next(s for s in feedback.category_scores if s.category == "Abstraction")
    assert abs_score.score >= 7


def test_evaluator_rewards_solid_keywords():
    """Mentioning SOLID principles should raise the SOLID score."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    feedback = evaluator.evaluate(
        problem,
        solution_text="single responsibility open closed liskov interface segregation dependency inversion",
        solution_code="",
    )

    solid_score = next(s for s in feedback.category_scores if s.category == "SOLID Principles")
    assert solid_score.score >= 7


def test_evaluator_handles_empty_solution():
    """An empty solution should not crash and should return low scores."""
    evaluator = RuleBasedFeedbackEvaluator()
    problem = make_problem()

    feedback = evaluator.evaluate(problem, solution_text="", solution_code="")

    assert feedback.overall_score < 5
    assert len(feedback.improvements) >= 1
