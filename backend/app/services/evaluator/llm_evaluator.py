import json
import re
from typing import Optional

import httpx

from ...config import settings
from ...schemas import CategoryScore, Feedback, ProblemOut
from .base import FeedbackEvaluator


class LLMFeedbackEvaluator(FeedbackEvaluator):
    """Evaluator that uses an LLM (OpenAI-compatible API) for feedback.

    The LLM is asked to return strict JSON matching the Feedback schema.
    If parsing fails, `evaluate` raises so the caller can fall back to the
    rule-based evaluator.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: Optional[int] = None,
    ):
        self.api_key = api_key or settings.LLM_API_KEY
        self.base_url = (base_url or settings.LLM_BASE_URL).rstrip("/")
        self.model = model or settings.LLM_MODEL
        self.timeout = timeout or settings.LLM_TIMEOUT

    def evaluate(
        self,
        problem: ProblemOut,
        solution_text: str,
        solution_code: str,
    ) -> Feedback:
        if not self.api_key:
            raise RuntimeError("LLM API key is not configured.")

        prompt = self._build_prompt(problem, solution_text, solution_code)
        raw = self._call_llm(prompt)
        return self._parse_feedback(raw)

    # ---- Prompt construction --------------------------------------------------

    def _build_prompt(self, problem: ProblemOut, solution_text: str, solution_code: str) -> str:
        requirements = "\n".join(f"- {r}" for r in problem.requirements)
        criteria = "\n".join(f"- {c}" for c in problem.evaluation_criteria)

        return f"""You are an expert Low-Level Design (LLD) reviewer. A learner has submitted a solution for the following design problem. Evaluate it honestly and constructively.

PROBLEM: {problem.title}
DESCRIPTION: {problem.description}

REQUIREMENTS:
{requirements}

EVALUATION CRITERIA:
{criteria}

LEARNER'S SOLUTION (prose):
\"\"\"
{solution_text}
\"\"\"

LEARNER'S CODE:
\"\"\"
{solution_code or '(no code provided)'}
\"\"\"

INSTRUCTIONS:
Return ONLY a single JSON object with this exact structure (no markdown, no explanation outside the JSON):
{{
  "overall_score": <number 0-10>,
  "summary": "<2-3 sentence overall assessment>",
  "strengths": ["<specific thing the solution does well>", ...],
  "improvements": ["<specific actionable suggestion>", ...],
  "category_scores": [
    {{"category": "Requirement Coverage", "score": <0-10>, "comment": "<short comment>"}},
    {{"category": "Responsibility Assignment", "score": <0-10>, "comment": "<short comment>"}},
    {{"category": "Abstraction", "score": <0-10>, "comment": "<short comment>"}},
    {{"category": "SOLID Principles", "score": <0-10>, "comment": "<short comment>"}},
    {{"category": "Relationships", "score": <0-10>, "comment": "<short comment>"}}
  ]
}}

Be specific and reference the learner's actual classes/decisions. There may be more than one valid solution; judge the quality of the design decisions, not whether it matches a reference exactly."""

    # ---- API call -------------------------------------------------------------

    def _call_llm(self, prompt: str) -> str:
        """Send the prompt to the OpenAI-compatible chat completions endpoint."""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert LLD code reviewer. Always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.3,
            "response_format": {"type": "json_object"},
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                return data["choices"][0]["message"]["content"]
        except httpx.HTTPError as exc:
            raise RuntimeError(f"LLM API request failed: {exc}") from exc
        except (KeyError, IndexError, ValueError) as exc:
            raise RuntimeError(f"Unexpected LLM response format: {exc}") from exc

    # ---- Response parsing -----------------------------------------------------

    @staticmethod
    def _parse_feedback(raw: str) -> Feedback:
        """Parse the LLM's JSON response into a Feedback object.

        The LLM is asked for pure JSON, but some models wrap it in code fences
        or add prose. We extract the first JSON object defensively.
        """
        text = raw.strip()
        # Remove markdown code fences if present
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)

        # Find the first '{' and last '}'
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end < start:
            raise ValueError("LLM response did not contain a JSON object.")
        json_str = text[start : end + 1]

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as exc:
            raise ValueError(f"LLM response was not valid JSON: {exc}") from exc

        category_scores = [
            CategoryScore(
                category=c.get("category", "Uncategorized"),
                score=float(c.get("score", 0)),
                comment=c.get("comment", ""),
            )
            for c in data.get("category_scores", [])
        ]

        return Feedback(
            overall_score=float(data.get("overall_score", 0)),
            summary=data.get("summary", ""),
            strengths=list(data.get("strengths", [])),
            improvements=list(data.get("improvements", [])),
            category_scores=category_scores,
            approach="llm",
        )
