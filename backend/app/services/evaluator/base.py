from abc import ABC, abstractmethod

from ...schemas import Feedback, ProblemOut


class FeedbackEvaluator(ABC):
    """Interface for evaluating a learner's LLD solution.

    Any evaluator (LLM-based, rule-based, or future approach) implements this
    single method. This keeps the rest of the system decoupled from *how*
    evaluation happens, which makes swapping or combining evaluators trivial.
    """

    @abstractmethod
    def evaluate(
        self,
        problem: ProblemOut,
        solution_text: str,
        solution_code: str,
    ) -> Feedback:
        """Evaluate the solution and return structured feedback.

        Args:
            problem: The problem being solved, including its evaluation criteria.
            solution_text: The learner's prose description of their design.
            solution_code: The learner's code snippets (classes/interfaces).

        Returns:
            A Feedback object with an overall score, strengths, improvements,
            and per-category scores.
        """
        raise NotImplementedError
