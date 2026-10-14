import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { AttemptSummary, Problem } from "../types";

interface ProblemDetailProps {
  problemId: number;
  onBack: () => void;
  onSubmitted: (attemptId: number) => void;
}

export default function ProblemDetail({
  problemId,
  onBack,
  onSubmitted,
}: ProblemDetailProps) {
  const [problem, setProblem] = useState<Problem | null>(null);
  const [history, setHistory] = useState<AttemptSummary[]>([]);
  const [solutionText, setSolutionText] = useState("");
  const [solutionCode, setSolutionCode] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .getProblem(problemId)
      .then(setProblem)
      .catch((e) => setError(e.message));
    api.listAttempts(problemId).then(setHistory).catch(() => {});
  }, [problemId]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!solutionText.trim()) {
      setError("Please describe your design before submitting.");
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      const attempt = await api.createAttempt(problemId, {
        solution_text: solutionText,
        solution_code: solutionCode,
      });
      onSubmitted(attempt.id);
    } catch (err: any) {
      setError(err.message || "Submission failed. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  if (error && !problem) {
    return (
      <div className="card mt-2" style={{ color: "var(--danger)" }}>
        {error}
      </div>
    );
  }

  if (!problem) {
    return <div className="spinner" style={{ marginTop: "3rem" }} />;
  }

  return (
    <div>
      <button className="btn-ghost" onClick={onBack} style={{ marginBottom: "1rem" }}>
        ← Back to problems
      </button>

      <div className="card mb-1">
        <div className="row space-between">
          <h1 style={{ margin: 0 }}>{problem.title}</h1>
          <span className={`badge badge-${problem.difficulty}`}>
            {problem.difficulty}
          </span>
        </div>
        <p style={{ marginTop: "0.8rem" }}>{problem.description}</p>

        <h3>Requirements</h3>
        <ul>
          {problem.requirements.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>

        {problem.hints.length > 0 && (
          <>
            <h3>Hints</h3>
            <ul>
              {problem.hints.map((h, i) => (
                <li key={i}>{h}</li>
              ))}
            </ul>
          </>
        )}

        <h3>Evaluation Criteria</h3>
        <ul>
          {problem.evaluation_criteria.map((c, i) => (
            <li key={i}>{c}</li>
          ))}
        </ul>
      </div>

      <h2>Your Solution</h2>
      <form onSubmit={handleSubmit}>
        <div className="card">
          <label>
            <strong>Design description</strong>
            <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)" }}>
              Explain your classes, responsibilities, relationships, and the
              trade-offs you considered.
            </p>
          </label>
          <textarea
            value={solutionText}
            onChange={(e) => setSolutionText(e.target.value)}
            rows={10}
            placeholder="Describe your design here..."
            style={{ marginBottom: "1rem" }}
          />

          <label>
            <strong>Code / class definitions</strong>
            <p style={{ fontSize: "0.9rem", color: "var(--ink-soft)" }}>
              Paste your interfaces, classes, and key methods (any language).
            </p>
          </label>
          <textarea
            value={solutionCode}
            onChange={(e) => setSolutionCode(e.target.value)}
            rows={12}
            placeholder="class ParkingLot { ... }"
            style={{ fontFamily: "Consolas, monospace" }}
          />

          {error && (
            <p style={{ color: "var(--danger)", marginTop: "1rem" }}>{error}</p>
          )}

          <div className="row space-between mt-2">
            <button
              type="button"
              className="btn-ghost"
              onClick={() => {
                setSolutionText("");
                setSolutionCode("");
              }}
            >
              Clear
            </button>
            <button type="submit" className="btn-primary" disabled={submitting}>
              {submitting ? "Evaluating..." : "Submit for Feedback"}
            </button>
          </div>
        </div>
      </form>

      {history.length > 0 && (
        <div className="mt-2">
          <h2>Previous Attempts</h2>
          <div className="card">
            {history.map((a) => (
              <div
                key={a.id}
                className="row space-between"
                style={{
                  padding: "0.6rem 0",
                  borderBottom: "1px solid var(--border)",
                }}
              >
                <div>
                  <strong>Attempt #{a.id}</strong>
                  <span style={{ marginLeft: "0.8rem", color: "var(--ink-soft)" }}>
                    {new Date(a.created_at).toLocaleString()}
                  </span>
                </div>
                <div className="row">
                  <span className={`badge badge-${a.status === "completed" ? "easy" : "hard"}`}>
                    {a.status}
                  </span>
                  {a.overall_score != null && (
                    <span
                      className="score-ring"
                      style={{
                        width: "44px",
                        height: "44px",
                        fontSize: "0.95rem",
                        background:
                          a.overall_score >= 7
                            ? "var(--green-dark)"
                            : a.overall_score >= 4
                            ? "#d4a017"
                            : "var(--danger)",
                      }}
                    >
                      {a.overall_score.toFixed(1)}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
