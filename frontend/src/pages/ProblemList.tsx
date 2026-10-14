import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { ProblemSummary } from "../types";

interface ProblemListProps {
  onSelect: (problemId: number) => void;
}

export default function ProblemList({ onSelect }: ProblemListProps) {
  const [problems, setProblems] = useState<ProblemSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .listProblems()
      .then(setProblems)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return <div className="spinner" style={{ marginTop: "3rem" }} />;
  }

  if (error) {
    return (
      <div className="card mt-2" style={{ color: "var(--danger)" }}>
        Failed to load problems: {error}
      </div>
    );
  }

  return (
    <div>
      <h1>Choose a Problem</h1>
      <p style={{ marginBottom: "1.5rem" }}>
        Pick a Low-Level Design problem to practice. You'll design a solution,
        submit it, and get structured feedback to improve.
      </p>
      <div className="grid-2">
        {problems.map((p) => (
          <div
            key={p.id}
            className="card card-hover"
            onClick={() => onSelect(p.id)}
          >
            <div className="row space-between">
              <h3 style={{ margin: 0 }}>{p.title}</h3>
              <span className={`badge badge-${p.difficulty}`}>
                {p.difficulty}
              </span>
            </div>
            <p style={{ marginTop: "0.6rem", marginBottom: 0 }}>
              {p.short_description}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
