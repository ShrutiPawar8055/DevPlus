import { useState } from "react";
import Header from "./components/Header";
import ProblemList from "./pages/ProblemList";
import ProblemDetail from "./pages/ProblemDetail";
import FeedbackView from "./pages/FeedbackView";

// Simple state-based navigation. No router dependency needed for an MVP.
type View =
  | { name: "list" }
  | { name: "detail"; problemId: number }
  | { name: "feedback"; attemptId: number; problemId: number };

export default function App() {
  const [view, setView] = useState<View>({ name: "list" });

  const goHome = () => setView({ name: "list" });
  const openProblem = (problemId: number) =>
    setView({ name: "detail", problemId });
  const openFeedback = (attemptId: number, problemId: number) =>
    setView({ name: "feedback", attemptId, problemId });

  return (
    <>
      <Header onHome={goHome} />
      <main className="container">
        {view.name === "list" && <ProblemList onSelect={openProblem} />}
        {view.name === "detail" && (
          <ProblemDetail
            problemId={view.problemId}
            onBack={goHome}
            onSubmitted={(attemptId) =>
              openFeedback(attemptId, view.problemId)
            }
          />
        )}
        {view.name === "feedback" && (
          <FeedbackView
            attemptId={view.attemptId}
            problemId={view.problemId}
            onBack={() => openProblem(view.problemId)}
            onTryAgain={() => openProblem(view.problemId)}
          />
        )}
      </main>
    </>
  );
}
