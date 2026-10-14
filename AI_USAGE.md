# AI Usage Notes

This document records the meaningful AI-assisted decisions made while building the LLD Practice Platform. For each, I note what was suggested, what was accepted or rejected, and why.

---

## 1. Evaluation strategy: LLM-only vs. hybrid (LLM + rule-based fallback)


**Decision: Rejected the LLM-only approach; accepted a hybrid design.**

**Why:** An LLM-only evaluator creates two problems for an MVP:
- It requires an API key to work at all, making the prototype un-runnable out of the box.
- It makes evaluation non-deterministic and hard to test.

Instead, I defined a `FeedbackEvaluator` interface with two implementations:
- `LLMFeedbackEvaluator` — uses an OpenAI-compatible API.
- `RuleBasedFeedbackEvaluator` — deterministic, keyword/heuristic-based scoring.

A `evaluate_with_fallback()` function tries the LLM first and falls back to the rule-based engine on any failure. This guarantees the learner *always* gets feedback while still using the LLM when available. The interface also makes it trivial to swap in a third evaluator later (e.g., a diagram parser).

---

## 2. Submission format: structured form vs. free text + code

**Suggestion:** Use a structured form where learners fill in fields per class (name, responsibilities, methods, relationships) — easier to evaluate deterministically.

**Decision: Accepted the text + code snippets approach over the structured form.**

**Why:** A structured form is rigid — it constrains how learners think about their design and doesn't handle unusual but valid designs well. Free prose + code snippets are more flexible and closer to how engineers actually document LLD. The evaluator handles this by combining heuristic signals (class count, keyword detection) with LLM qualitative assessment.

The trade-off is that deterministic evaluation is weaker on free-text, but the LLM compensates, and the rule-based engine still catches obvious gaps (no classes, no interfaces, missing SOLID vocabulary).

---

## 3. Feedback storage: separate `Feedback` table vs. JSON column on `Attempt`

**Suggestion:** Create a normalized `Feedback` table with `category_scores` in a separate table for clean relational queries.

**Decision: Rejected normalization; accepted a JSON column on `Attempt`.**

**Why:** The feedback shape will evolve (new categories, new fields like "trade-offs" or "reference examples"). A normalized schema would require a migration every time the feedback structure changes. Storing feedback as a JSON string on `Attempt` lets the schema evolve freely. The `AttemptRepository.parse_feedback()` method handles deserialization, and if we ever need to query across feedback fields, we can extract them into columns later.

This is a deliberate bet on flexibility over queryability, appropriate for an MVP.

---

## 4. Synchronous vs. async evaluation

**Suggestion:** Make evaluation async with a background worker + status polling, since LLMs can be slow.

**Decision: Accepted synchronous evaluation for the MVP; documented the async path as a future improvement.**

**Why:** The assignment explicitly says "do not turn the assignment into a distributed-systems project." Synchronous evaluation keeps the code simple and the request/response cycle straightforward. The `Attempt` model already has a `status` field (`pending → evaluating → completed/failed`), so moving to async later is a matter of changing the service to return the attempt in `evaluating` status and running the evaluator in a background task. No schema changes needed.

For local development and a small number of users, synchronous is perfectly fine.

---

## 5. Deterministic vs. LLM scoring responsibilities

**Suggestion:** Let the LLM produce the entire feedback including numeric scores.

**Decision: Split responsibilities — deterministic checks for measurable signals, LLM for qualitative reasoning.**

**Why:** Numeric scores from an LLM alone are inconsistent (same input can yield different scores). Deterministic checks give stable, explainable scores:
- **Requirement coverage** → keyword overlap with requirements (deterministic)
- **Responsibility assignment** → class/interface count (deterministic)
- **Abstraction** → presence of `interface`/`abstract` keywords (deterministic)
- **SOLID principles** → SOLID vocabulary detection (deterministic)
- **Relationships** → relationship keyword detection (deterministic)

The LLM adds value in the *comments* and *suggestions* — explaining *why* a score is what it is and giving specific, actionable advice tied to the learner's actual classes. This combination gives both consistency and helpfulness.

---

## Summary

AI was used as a design partner for architecture decisions, not as a code-generation black box. The key pattern across all decisions: **favor interfaces and abstractions that keep options open**, so the prototype can grow (new evaluators, new submission formats, async evaluation) without rewriting the core.
