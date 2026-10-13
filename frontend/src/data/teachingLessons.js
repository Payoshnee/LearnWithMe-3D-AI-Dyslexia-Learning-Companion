
/**
 * LearnWithMe
 * Wendy — Learning Buddy
 *
 * Friendly, structured teaching curriculum.
 *
 * 22 words
 * 3 levels
 * 4 interactive steps per lesson
 * 1 optional sentence activity
 *
 * IMPORTANT:
 * The backend currently validates four steps.
 * Sentence activities are prepared for later use.
 */

export const teachingWords = [
  // LEVEL 1 — First Words
  {
    word: "CAT",
    sounds: ["c", "a", "t"],
    level: 1,
    meaning: "A cat is a furry animal that says meow.",
    sentence: "The cat can sit.",
  },
  {
    word: "SUN",
    sounds: ["s", "u", "n"],
    level: 1,
    meaning: "The sun gives us light and warmth.",
    sentence: "The sun is hot.",
  },
  {
    word: "MAT",
    sounds: ["m", "a", "t"],
    level: 1,
    meaning: "A mat is something we can sit or stand on.",
    sentence: "The cat sat on the mat.",
  },
  {
    word: "SAT",
    sounds: ["s", "a", "t"],
    level: 1,
    meaning: "Sat means someone was sitting.",
    sentence: "The cat sat.",
  },
  {
    word: "PIN",
    sounds: ["p", "i", "n"],
    level: 1,
    meaning: "A pin is a small object used to hold things together.",
    sentence: "I see a pin.",
  },
  {
    word: "TIN",
    sounds: ["t", "i", "n"],
    level: 1,
    meaning: "A tin is a small metal container.",
    sentence: "The tin is red.",
  },
  {
    word: "PAN",
    sounds: ["p", "a", "n"],
    level: 1,
    meaning: "A pan is used for cooking food.",
    sentence: "The pan is hot.",
  },
  {
    word: "BAT",
    sounds: ["b", "a", "t"],
    level: 1,
    meaning: "A bat can be an animal that flies at night.",
    sentence: "I see a bat.",
  },

  // LEVEL 2 — Growing Reader
  {
    word: "DOG",
    sounds: ["d", "o", "g"],
    level: 2,
    meaning: "A dog is an animal that often barks.",
    sentence: "The dog can run.",
  },
  {
    word: "PIG",
    sounds: ["p", "i", "g"],
    level: 2,
    meaning: "A pig is a farm animal with a snout.",
    sentence: "The pig is big.",
  },
  {
    word: "HEN",
    sounds: ["h", "e", "n"],
    level: 2,
    meaning: "A hen is a female chicken.",
    sentence: "The hen is red.",
  },
  {
    word: "PEN",
    sounds: ["p", "e", "n"],
    level: 2,
    meaning: "A pen helps us write words and letters.",
    sentence: "I have a pen.",
  },
  {
    word: "BED",
    sounds: ["b", "e", "d"],
    level: 2,
    meaning: "A bed is where we rest and sleep.",
    sentence: "The bed is soft.",
  },
  {
    word: "RED",
    sounds: ["r", "e", "d"],
    level: 2,
    meaning: "Red is a colour, like a ripe tomato.",
    sentence: "The hat is red.",
  },
  {
    word: "CUP",
    sounds: ["c", "u", "p"],
    level: 2,
    meaning: "A cup holds water, milk, or other drinks.",
    sentence: "The cup is full.",
  },
  {
    word: "BUS",
    sounds: ["b", "u", "s"],
    level: 2,
    meaning: "A bus is a large vehicle that carries people.",
    sentence: "The bus is big.",
  },

  // LEVEL 3 — Sound Teams
  {
    word: "SHIP",
    sounds: ["sh", "i", "p"],
    level: 3,
    meaning: "A ship is a large boat.",
    sentence: "The ship is big.",
  },
  {
    word: "SHOP",
    sounds: ["sh", "o", "p"],
    level: 3,
    meaning: "A shop is a place where we buy things.",
    sentence: "We go to the shop.",
  },
  {
    word: "FISH",
    sounds: ["f", "i", "sh"],
    level: 3,
    meaning: "A fish is an animal that lives in water.",
    sentence: "The fish can swim.",
  },
  {
    word: "CHIP",
    sounds: ["ch", "i", "p"],
    level: 3,
    meaning: "A chip can be a small piece of something.",
    sentence: "I have a chip.",
  },
  {
    word: "CHAT",
    sounds: ["ch", "a", "t"],
    level: 3,
    meaning: "To chat means to talk with someone.",
    sentence: "We like to chat.",
  },
  {
    word: "THIN",
    sounds: ["th", "i", "n"],
    level: 3,
    meaning: "Thin means not very thick.",
    sentence: "The book is thin.",
  },
];

export const teachingLevels = [
  {
    id: 1,
    title: "First Words",
    description: "Learn simple words with three sounds.",
  },
  {
    id: 2,
    title: "Growing Reader",
    description: "Practise more letters and short vowels.",
  },
  {
    id: 3,
    title: "Sound Teams",
    description: "Learn sounds made by two letters together.",
  },
];

export function getTeachingWords(level = 1) {
  return teachingWords.filter(
    (item) => item.level === Number(level)
  );
}

export function getTeachingWord(word) {
  const query = String(word || "").toLowerCase();

  return (
    teachingWords.find(
      (item) => item.word.toLowerCase() === query
    ) || null
  );
}

/**
 * Friendly pronunciation labels.
 *
 * These are narration labels, not a full
 * phonetic transcription system.
 */
const SOUND_LABELS = {
  a: "short a",
  b: "b",
  c: "k",
  d: "d",
  e: "short e",
  f: "f",
  g: "g",
  h: "h",
  i: "short i",
  m: "m",
  n: "n",
  o: "short o",
  p: "p",
  r: "r",
  s: "s",
  t: "t",
  u: "short u",
  sh: "sh",
  ch: "ch",
  th: "th",
};

function getSoundLabel(symbol) {
  return SOUND_LABELS[symbol] || symbol;
}

function getFirstLetterHint(word) {
  return (
    `Look at the beginning of ${word}. ` +
    `The first letter is ${word.charAt(0)}. ` +
    "You can say its name or type it."
  );
}

function getSoundHint(word, symbol) {
  const sound = getSoundLabel(symbol);

  return (
    `In ${word}, the first sound is ${sound}. ` +
    "Listen again, then try saying the sound. " +
    "You can also type the sound if you prefer."
  );
}

function getBlendHint(word) {
  return (
    `Look at ${word}. Let's say the sounds slowly ` +
    "and join them together. " +
    `The sounds make ${word}.`
  );
}

function getReadHint(word) {
  return (
    `Take your time. Look from left to right. ` +
    `The word is ${word}. You can try again.`
  );
}

export function createTeachingLesson(item) {
  if (!item) return null;

  const word = item.word.toUpperCase();
  const firstLetter = word.charAt(0);
  const firstSound = item.sounds[0];
  const firstSoundLabel = getSoundLabel(firstSound);
  const isDigraph = item.sounds.some(
    (sound) => sound.length > 1
  );

  return {
    id: word.toLowerCase(),
    word,
    level: item.level,
    sentence: item.sentence,
    meaning: item.meaning,

    steps: [
      {
        id: "recognize",
        title: "Meet the Word",
        type: "recognition",

        display:
          `Look at ${word}. ` +
          `Can you find the letter ${firstLetter}?`,

        speak:
          `Hello, my little learner! ` +
          `Today we're learning ${word}. ` +
          `${item.meaning} ` +
          `Let's look at the letters together. ` +
          `Can you find the letter ${firstLetter}? ` +
          "Say the letter's name or type it.",

        expected: firstLetter,
        hint: getFirstLetterHint(word),

        encouragement:
          `Wonderful! You found the first letter of ${word}!`,
      },

      {
        id: "sounds",
        title: "Learn the Sounds",
        type: "phonics",

        display: isDigraph
          ? `Listen to the sound groups in ${word}.`
          : `Listen to each letter sound in ${word}.`,

        speak:
          `Lovely work! ` +
          `Now let's listen to the sounds in ${word}. ` +
          `The first sound is ${firstSoundLabel}. ` +
          "Listen carefully and try saying that sound. " +
          "You can repeat it as many times as you like.",

        sounds: item.sounds,
        expected: firstSound,

        hint: getSoundHint(word, firstSound),

        encouragement:
          "Good effort! You're learning how letters make sounds.",
      },

      {
        id: "blend",
        title: "Blend the Sounds",
        type: "blending",

        display:
          `Put the sounds together to make ${word}.`,

        speak:
          `You're doing well! ` +
          `Now let's put the sounds together. ` +
          `Listen to each sound in ${word}. ` +
          `Now join them slowly to make ${word}. ` +
          "Try saying the whole word.",

        sounds: item.sounds,
        expected: word,

        hint: getBlendHint(word),

        encouragement:
          `Wonderful blending! You made the word ${word}!`,
      },

      {
        id: "read",
        title: "Read the Word",
        type: "reading",

        display: `Can you read ${word}?`,

        speak:
          `We've learned the letters and the sounds. ` +
          `Now it's time to read the whole word. ` +
          `Look carefully at ${word}. ` +
          "Read it when you're ready. " +
          "There's no hurry.",

        expected: word,

        hint: getReadHint(word),

        encouragement:
          `Amazing effort! You finished learning ${word}! ` +
          "I'm proud of how hard you tried.",
      },

      // Prepared for a future backend upgrade.
      // Not currently part of the four-step validator.
      {
        id: "sentence",
        title: "Use the Word",
        type: "sentence",

        display: item.sentence,

        speak:
          `Let's use ${word} in a sentence. ` +
          `${item.sentence} ` +
          "Listen to the sentence. " +
          "Then read it with me if you would like.",

        expected: item.sentence,

        hint:
          `Listen to this sentence again. ` +
          item.sentence,

        encouragement:
          "That was lovely reading! Keep practising.",
      },
    ],
  };
}

export const teachingLessons = Object.fromEntries(
  teachingWords.map((item) => [
    item.word.toLowerCase(),
    createTeachingLesson(item),
  ])
);
