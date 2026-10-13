import test from 'node:test'
import assert from 'node:assert/strict'

class MockUtterance {
  constructor(text) { this.text = text }
}

test('server speech failure falls back to a selected English browser voice', async () => {
  const spoken = []
  globalThis.fetch = async () => ({ ok: false, status: 503, blob: async () => new Blob() })
  globalThis.window = {
    SpeechSynthesisUtterance: MockUtterance,
    speechSynthesis: {
      cancel() {},
      getVoices: () => [{ name: 'Microsoft Aria Online', lang: 'en-US' }],
      speak(utterance) { spoken.push(utterance); queueMicrotask(() => utterance.onend()) },
    },
  }
  globalThis.SpeechSynthesisUtterance = MockUtterance
  const { speakLearningText } = await import('../src/audio/learningAudio.js')
  assert.equal(await speakLearningText('Try the next word.', 'wendy'), 'browser')
  assert.equal(spoken[0].text, 'Try the next word.')
  assert.equal(spoken[0].voice.name, 'Microsoft Aria Online')
})

test('answer normalization removes IPA presentation marks', async () => {
  const { normalizeAnswer } = await import('../src/audio/learningAudio.js')
  assert.equal(normalizeAnswer(' /S/ '), 's')
})
