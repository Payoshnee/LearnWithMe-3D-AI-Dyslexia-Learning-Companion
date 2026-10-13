export default function TeachingBoard({ open, board, activeSyllable }) {
  if (!open) {
    return null;
  }

  const syllables = board?.syllables || [];
  const isQuiz = board?.type === "quiz";
  const isStats = board?.type === "stats";

  return (
    <aside className="teaching-board" aria-label="Doodle teaching board">
      <p className="eyebrow">{isStats ? "Progress" : isQuiz ? "Quiz" : "Pronunciation"}</p>
      <h2>{isStats ? "Your progress" : isQuiz ? "Answer by voice" : "Say it with me"}</h2>
      {isStats ? (
        <>
          <p className="board-word">{board?.accuracy ?? 0}%</p>
          <p className="board-copy">Quiz accuracy</p>
          <div className="syllable-row">
            {(board?.trickyWords || []).map((word) => (
              <span key={word}>{word}</span>
            ))}
          </div>
          <p className="board-feedback">Next practice: {board?.nextPractice}</p>
        </>
      ) : isQuiz ? (
        <>
          <p className="board-copy">{board?.question}</p>
          <ol className="quiz-options">
            {(board?.options || []).map((option, index) => (
              <li className={index === board?.selectedIndex ? "active" : ""} key={option}>
                {"ABCD"[index]}. {option}
              </li>
            ))}
          </ol>
          {board?.selectedAnswer && (
            <p className="board-copy">I heard: {board.selectedAnswer}</p>
          )}
          {board?.feedback && <p className="board-feedback">{board.feedback}</p>}
        </>
      ) : (
        <>
          <p className="board-word">{board?.word}</p>
          <div className="syllable-row">
            {syllables.map((syllable, index) => (
              <span
                className={
                  index === activeSyllable || syllable === board?.weakSyllable ? "active" : ""
                }
                key={`${syllable}-${index}`}
              >
                {syllable}
              </span>
            ))}
          </div>
          {typeof board?.score === "number" && (
            <p className="board-feedback">
              Score: {board.score}% {board.passed ? "Clear" : `Practice ${board.weakSyllable}`}
            </p>
          )}
          <p className="board-copy">
            {board?.prompt || "Watch the doodle point, then try the word slowly."}
          </p>
        </>
      )}
    </aside>
  );
}
