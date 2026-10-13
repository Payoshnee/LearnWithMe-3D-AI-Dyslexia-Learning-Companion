export const LEVELS = [
  { id: 1, name: 'First sounds', letters: ['m','s','a','t'], words: ['mat','sat'] },
  { id: 2, name: 'Build and blend', letters: ['p','i','n','d'], words: ['pin','dip','sit'] },
  { id: 3, name: 'Growing reader', letters: ['c','o','g','f'], words: ['cat','dog','fog'] },
]

export const shuffle = (items, random = Math.random) => [...items]
  .map(value => ({ value, order: random() }))
  .sort((a, b) => a.order - b.order)
  .map(item => item.value)

export const isBuiltWordCorrect = (letters, word) => letters.join('').toLowerCase() === word.toLowerCase()
export const traceIsReady = points => points.length >= 14
export const isMemoryMatch = (a, b) => Boolean(a && b && a.pairId === b.pairId && a.id !== b.id)
export const normalizePhonicsAnswer = value => String(value || '').toLowerCase().replace(/[\/\s]/g, '').replace(/[^a-z]/g, '')

export function makeMemoryDeck(letters, random = Math.random) {
  return shuffle(letters.flatMap(letter => [
    { id: `${letter}-letter`, pairId: letter, kind: 'letter', label: letter.toUpperCase() },
    { id: `${letter}-sound`, pairId: letter, kind: 'sound', label: `/${letter}/` },
  ]), random)
}

export function makeCatchRound(target, letters, random = Math.random) {
  const options = shuffle([...new Set([target, ...letters.filter(x => x !== target)])], random).slice(0, 4)
  return { target, options, correctIndex: options.indexOf(target) }
}
