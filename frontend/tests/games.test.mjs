import test from 'node:test'
import assert from 'node:assert/strict'
import { isBuiltWordCorrect, isMemoryMatch, makeCatchRound, makeMemoryDeck, normalizePhonicsAnswer, traceIsReady } from '../src/games/gameLogic.js'

test('IPA slashes and spaces are removed before validation', () => {
  assert.equal(normalizePhonicsAnswer(' /M/ '), 'm')
})
test('word building validates the full ordered word', () => {
  assert.equal(isBuiltWordCorrect(['c','a','t'], 'cat'), true)
  assert.equal(isBuiltWordCorrect(['a','c','t'], 'cat'), false)
})
test('tracing requires a meaningful pointer path', () => {
  assert.equal(traceIsReady(Array(14).fill([0, 0])), true)
  assert.equal(traceIsReady(Array(5).fill([0, 0])), false)
})
test('memory cards match only distinct cards in the same pair', () => {
  const deck = makeMemoryDeck(['m','s'], () => 0.5)
  assert.equal(deck.length, 4)
  assert.equal(isMemoryMatch(deck.find(x => x.id === 'm-letter'), deck.find(x => x.id === 'm-sound')), true)
  assert.equal(isMemoryMatch(deck[0], deck[0]), false)
})
test('catch round always contains the target and records its lane', () => {
  const round = makeCatchRound('s', ['m','a','t'], () => 0.5)
  assert.equal(round.options[round.correctIndex], 's')
})
