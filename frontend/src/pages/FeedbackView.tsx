import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { Attempt } from "../types";

interface FeedbackViewProps {
  attemptId: number;
  problemId: number;
  onBack: () => void;
  onTryAgain: () => void;
}

export default function FeedbackView({
  attemptId,
  onBack,
  onTryAgain,
}: FeedbackViewProps) {
  const [attempt, setAttempt] = useState<Attempt | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getAttempt(attemptId)
      .then(setAttempt)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [attemptId]);

  if (loading) {
    return <div className="spinner" style={{ marginTop: "3rem" }} />;
  }

  if (error || !attempt) {
    return (
      <div className="card mt-2" style={{ color: "var(--danger)" }}>
        {error || "Attempt not found."}
      </div>
    );
  }

  const feedback = attempt.feedback;
  const scoreClass =
    (attempt.overall_score ?? 0) >= 7
      ? "score-high"
      : (attempt.overall_score ?? 0) >= 4
      ? "score-mid"
      : "score-low";

  return (
    <div>
      <button className="btn-ghost" onClick={onBack} style={{ marginBottom: "1rem" }}>
        ← Back to problem
      </button>

      {attempt.status === "failed" && (
        <div className="card" style={{ color: "var(--danger)", marginBottom: "1rem" }}>
          <strong>Evaluation failed:</strong> {attempt.error_message}
        </div>
      )}

      {feedback && (
        <>
          <div className="card mb-1">
            <div className="row space-between">
              <div>
                <h1 style={{ margin: 0 }}>Feedback</h1>
                <p style={{ margin: "0.3rem 0 0" }}>
                  Evaluated via{" "}
                  <span className="tag">
                    {feedback.approach === "llm" ? "AI (LLM)" : "rule-based engine"}
                  </span>
                </p>
              </div>
              <div className={`score-ring ${scoreClass}`}>
                {attempt.overall_score?.toFixed(1)}
              </div>
            </div>
            <p style={{ marginTop: "1rem", fontSize: "1.05rem" }}>
              {feedback.summary}
            </p>
          </div>

          <div className="feedback-section">
            <h3 style={{ color: "var(--green-dark)" }}>Strengths</h3>
            <ul className="strengths-list">
              {feedback.strengths.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>

          <div className="feedback-section">
            <h3 style={{ color: "var(--danger)" }}>Areas to Improve</h3>
            <ul className="improvements-list">
              {feedback.improvements.map((s, i) => (
                <li key={i}>{s}</li>
              ))}
            </ul>
          </div>

          <div className="feedback-section">
            <h3>Category Scores</h3>
            {feedback.category_scores.map((c, i) => (
              <div
                key={i}
                style={{
                  marginBottom: "0.8rem",
                  paddingBottom: "0.8rem",
                  borderBottom:
                    i < feedback.category_scores.length - 1
                      ? "1px solid var(--border)"
                      : "none",
                }}
              >
                <div className="row space-between">
                  <strong>{c.category}</strong>
                  <span
                    style={{
                      fontWeight: 700,
                      color:
                        c.score >= 7
                          ? "var(--green-dark)"
                          : c.score >= 4
                          ? "#d4a017"
                          : "var(--danger)",
                    }}
                  >
                    {c.score.toFixed(1)}/10
                  </span>
                </div>
                <p style={{ margin: "0.3rem 0 0", fontSize: "0.95rem" }}>
                  {c.comment}
                </p>
              </div>
            ))}
          </div>

          <div className="feedback-section">
            <h3>Your Submission</h3>
            <p style={{ whiteSpace: "pre-wrap" }}>{attempt.solution_text}</p>
            {attempt.solution_code && (
              <div className="code-block">{attempt.solution_code}</div>
            )}
          </div>

          <div className="row" style={{ marginTop: "1.5rem" }}>
            <button className="btn-primary" onClick={onTryAgain}>
              Try Again
            </button>
            <button className="btn-ghost" onClick={onBack}>
              Back to Problem
            </button>
          </div>
        </>
      )}
    </div>
  );
}
