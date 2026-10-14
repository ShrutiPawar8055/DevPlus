// Domain types shared across the frontend, mirroring the backend Pydantic schemas.

export interface ProblemSummary {
  id: number;
  title: string;
  slug: string;
  difficulty: "easy" | "medium" | "hard";
  short_description: string;
}

export interface Problem extends ProblemSummary {
  description: string;
  requirements: string[];
  hints: string[];
  evaluation_criteria: string[];
}

export interface CategoryScore {
  category: string;
  score: number;
  comment: string;
}

export interface Feedback {
  overall_score: number;
  summary: string;
  strengths: string[];
  improvements: string[];
  category_scores: CategoryScore[];
  approach: "llm" | "rule_based";
}

export interface AttemptSummary {
  id: number;
  problem_id: number;
  status: "pending" | "evaluating" | "completed" | "failed";
  overall_score: number | null;
  created_at: string;
}

export interface Attempt extends AttemptSummary {
  solution_text: string;
  solution_code: string;
  feedback: Feedback | null;
  error_message: string | null;
}

export interface AttemptCreate {
  solution_text: string;
  solution_code: string;
}
