
/**
 * LearnWithMe — Practice Word Bank
 *
 * Wendy teaches these words.
 * Bob helps the learner practise them.
 *
 * Each word has a learning level and
 * simple activities with answer checking.
 */

export const practiceWords = [
  // LEVEL 1 — Simple CVC words
  { word: "CAT", sounds: ["c", "a", "t"], level: 1 },
  { word: "BAT", sounds: ["b", "a", "t"], level: 1 },
  { word: "MAT", sounds: ["m", "a", "t"], level: 1 },
  { word: "SAT", sounds: ["s", "a", "t"], level: 1 },
  { word: "SUN", sounds: ["s", "u", "n"], level: 1 },
  { word: "PIN", sounds: ["p", "i", "n"], level: 1 },
  { word: "TIN", sounds: ["t", "i", "n"], level: 1 },
  { word: "PAN", sounds: ["p", "a", "n"], level: 1 },

  // LEVEL 2 — More CVC words
  { word: "DOG", sounds: ["d", "o", "g"], level: 2 },
  { word: "PIG", sounds: ["p", "i", "g"], level: 2 },
  { word: "HEN", sounds: ["h", "e", "n"], level: 2 },
  { word: "PEN", sounds: ["p", "e", "n"], level: 2 },
  { word: "BED", sounds: ["b", "e", "d"], level: 2 },
  { word: "RED", sounds: ["r", "e", "d"], level: 2 },
  { word: "CUP", sounds: ["c", "u", "p"], level: 2 },
  { word: "BUS", sounds: ["b", "u", "s"], level: 2 },

  // LEVEL 3 — Digraphs and blending
  { word: "SHIP", sounds: ["sh", "i", "p"], level: 3 },
  { word: "SHOP", sounds: ["sh", "o", "p"], level: 3 },
  { word: "FISH", sounds: ["f", "i", "sh"], level: 3 },
  { word: "CHIP", sounds: ["ch", "i", "p"], level: 3 },
  { word: "CHAT", sounds: ["ch", "a", "t"], level: 3 },
  { word: "THIN", sounds: ["th", "i", "n"], level: 3 },
];

export const practiceTypes = [
  {
    id: "first-letter",
    title: "Find the First Letter",
    instruction: "Which letter comes first?",
  },
  {
    id: "spell",
    title: "Spell the Word",
    instruction: "Can you spell this word?",
  },
  {
    id: "read",
    title: "Read the Word",
    instruction: "Read this word aloud or type it.",
  },
];

export function getWordsForLevel(level = 1) {
  return practiceWords.filter(
    (item) => item.level === Number(level)
  );
}

export function getPracticeQuestion(word, type) {
  const target = word.word.toUpperCase();

  switch (type) {
    case "first-letter":
      return {
        question: `Which letter starts the word ${target}?`,
        answer: target[0],
        hint: `Look at the beginning of ${target}.`,
      };

    case "spell":
      return {
        question: `Can you spell ${target}?`,
        answer: target,
        hint: `The letters are ${target.split("").join(", ")}.`,
      };

    case "read":
      return {
        question: `Try reading the word ${target}.`,
        answer: target,
        hint: `Let's say it slowly: ${word.sounds.join(" - ")}.`,
      };

    default:
      return null;
  }
}

export function checkPracticeAnswer(
  userAnswer,
  expectedAnswer
) {
  const normalize = (value) =>
    String(value || "")
      .toUpperCase()
      .replace(/[^A-Z]/g, "");

  return normalize(userAnswer) === normalize(expectedAnswer);
}
