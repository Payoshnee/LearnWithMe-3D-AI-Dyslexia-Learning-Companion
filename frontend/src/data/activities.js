export const lessons = [
  { id: 'cat', title: 'Meet CAT', word: 'CAT', sounds: ['/k/', '/a/', '/t/'], steps: [
    ['recognize', 'Can you find the letter C in CAT?', ['c', 'see', 'letter c']],
    ['sounds', 'C says /k/. What sound does C make?', ['k', 'kuh', '/k/']],
    ['blend', 'Let’s blend it: /k/ /a/ /t/. Type CAT when you are ready.', ['cat']],
    ['read', 'Wonderful. Can you read the word CAT?', ['cat']],
  ] },
  { id: 'sun', title: 'Meet SUN', word: 'SUN', sounds: ['/s/', '/u/', '/n/'], steps: [
    ['recognize', 'Can you find the letter S in SUN?', ['s', 'ess', 'letter s']],
    ['sounds', 'S says /s/. What sound does S make?', ['s', 'sss', '/s/']],
    ['blend', 'Let’s blend it: /s/ /u/ /n/. Type SUN when you are ready.', ['sun']],
    ['read', 'Great! Can you read the word SUN?', ['sun']],
  ] },
]
export const games = [
  { id: 'match', name: 'Match the Sound', prompt: 'Which letter says /m/?', answer: 'M', choices: ['S', 'M', 'T'] },
  { id: 'build', name: 'Build the Word', prompt: 'Put the letters in order to build CAT.', answer: 'CAT', choices: ['T', 'C', 'A'] },
  { id: 'begin', name: 'Beginning Sound', prompt: 'Which word starts with /d/?', answer: 'DOG', choices: ['SUN', 'DOG', 'CAT'] },
]
