// Thin API client that wraps fetch and throws on non-2xx responses.
import type {
  Attempt,
  AttemptCreate,
  AttemptSummary,
  Problem,
  ProblemSummary,
} from "../types";

const BASE = "/api";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  listProblems: () => request<ProblemSummary[]>("/problems"),
  getProblem: (id: number) => request<Problem>(`/problems/${id}`),
  createAttempt: (problemId: number, data: AttemptCreate) =>
    request<Attempt>(`/problems/${problemId}/attempts`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  getAttempt: (id: number) => request<Attempt>(`/attempts/${id}`),
  listAttempts: (problemId: number) =>
    request<AttemptSummary[]>(`/problems/${problemId}/attempts`),
};
