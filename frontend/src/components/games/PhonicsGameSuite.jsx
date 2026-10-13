import { useMemo, useRef, useState } from 'react'
import { Headphones, RotateCcw, Sparkles, Volume2 } from 'lucide-react'
import { playPhoneme, speakLearningText } from '../../audio/learningAudio.js'
import { LEVELS, isBuiltWordCorrect, isMemoryMatch, makeCatchRound, makeMemoryDeck, shuffle, traceIsReady } from '../../games/gameLogic.js'

const GAME_NAMES = { trace: 'Letter tracing', build: 'Word builder', memory: 'Memory match', catch: 'Letter catch' }

function SoundButton({ letter, onError }) {
  const play = async event => {
    event.stopPropagation()
    try { await playPhoneme(letter) } catch (error) { onError(error.message) }
  }
  return <button className="sound-chip" onClick={play} aria-label={`Play the sound ${letter}`}><Volume2 size={17}/> /{letter}/</button>
}

function TraceGame({ level, onComplete, onError }) {
  const canvasRef = useRef(null), pointsRef = useRef([]), drawingRef = useRef(false)
  const [letterIndex, setLetterIndex] = useState(0), [feedback, setFeedback] = useState('Trace over the guide. Any careful attempt counts.')
  const letter = level.letters[letterIndex]
  const position = event => {
    const canvas = canvasRef.current, rect = canvas.getBoundingClientRect()
    const point = event.touches?.[0] || event
    return [(point.clientX - rect.left) * canvas.width / rect.width, (point.clientY - rect.top) * canvas.height / rect.height]
  }
  const start = event => { event.preventDefault(); drawingRef.current=true; pointsRef.current = [position(event)] }
  const move = event => {
    if (!drawingRef.current||!pointsRef.current.length) return
    event.preventDefault(); const next = position(event), previous = pointsRef.current.at(-1); pointsRef.current.push(next)
    const ctx = canvasRef.current.getContext('2d'); ctx.strokeStyle='#f59e0b';ctx.lineWidth=13;ctx.lineCap='round';ctx.beginPath();ctx.moveTo(...previous);ctx.lineTo(...next);ctx.stroke()
  }
  const clear = () => { const c=canvasRef.current;c.getContext('2d').clearRect(0,0,c.width,c.height);pointsRef.current=[];drawingRef.current=false;setFeedback('Try again at your own pace.') }
  const check = () => {
    if (!traceIsReady(pointsRef.current)) { setFeedback('Add a little more to your trace. There is no penalty.'); return }
    if (letterIndex < level.letters.length - 1) { setFeedback('Lovely tracing! Here is the next letter.'); setLetterIndex(x=>x+1); clear() }
    else { setFeedback('Tracing complete!'); onComplete('trace') }
  }
  return <div className="play-area"><div className="game-instruction"><h2>Trace lowercase {letter}</h2><SoundButton letter={letter} onError={onError}/></div><div className="trace-wrap"><span aria-hidden="true">{letter}</span><canvas ref={canvasRef} width="360" height="280" aria-label={`Tracing canvas for letter ${letter}`} onPointerDown={start} onPointerMove={move} onPointerUp={()=>drawingRef.current=false} onPointerLeave={()=>drawingRef.current=false}/></div><div className="game-controls"><button onClick={check}>I finished this trace</button><button className="quiet" onClick={clear}><RotateCcw size={16}/> Clear</button></div><p className="gentle-feedback" role="status">{feedback}</p></div>
}

function BuildGame({ level, onComplete, onError }) {
  const [wordIndex,setWordIndex]=useState(0), [built,setBuilt]=useState([]), [feedback,setFeedback]=useState('Choose or drag letters into the boxes.')
  const word=level.words[wordIndex], choices=useMemo(()=>shuffle(word.split('')),[word])
  const add=letter=>{ if(built.length<word.length)setBuilt(value=>[...value,letter]) }
  const check=()=>{ if(!isBuiltWordCorrect(built,word)){setFeedback('Almost there. Move the letters and try again—your score never goes down.');return} if(wordIndex<level.words.length-1){setFeedback('You built it! Try the next word.');setWordIndex(x=>x+1);setBuilt([])}else{setFeedback('Word building complete!');onComplete('build')} }
  const hear=async()=>{try{await speakLearningText(word,'bob')}catch(error){onError(error.message)}}
  return <div className="play-area"><div className="game-instruction"><h2>Build “{word}”</h2><button className="sound-chip" onClick={hear}><Headphones size={17}/> Hear word</button></div><div className="word-slots" onDragOver={e=>e.preventDefault()} onDrop={e=>add(e.dataTransfer.getData('text/plain'))}>{word.split('').map((_,i)=><span key={i}>{built[i]?.toUpperCase()||'_'}</span>)}</div><div className="letter-bank">{choices.map((letter,i)=><button key={`${letter}-${i}`} draggable onDragStart={e=>e.dataTransfer.setData('text/plain',letter)} onClick={()=>add(letter)} disabled={built.length>=word.length}>{letter.toUpperCase()}</button>)}</div><div className="game-controls"><button onClick={check}>Check word</button><button className="quiet" onClick={()=>setBuilt([])}>Start this word again</button></div><p className="gentle-feedback" role="status">{feedback}</p></div>
}

function MemoryGame({ level, onComplete, onError }) {
  const [deck,setDeck]=useState(()=>makeMemoryDeck(level.letters)),[open,setOpen]=useState([]),[matched,setMatched]=useState([]),[feedback,setFeedback]=useState('Match each letter with its sound card.')
  const flip=async card=>{if(open.length===2||matched.includes(card.pairId)||open.some(x=>x.id===card.id))return;const next=[...open,card];setOpen(next);if(card.kind==='sound')try{await playPhoneme(card.pairId)}catch(e){onError(e.message)}if(next.length===2){if(isMemoryMatch(...next)){const done=[...matched,card.pairId];setMatched(done);setFeedback('A match!');setOpen([]);if(done.length===level.letters.length)onComplete('memory')}else{setFeedback('Those are different. They will turn back so you can remember them.');setTimeout(()=>setOpen([]),850)}}}
  const reset=()=>{setDeck(makeMemoryDeck(level.letters));setOpen([]);setMatched([]);setFeedback('New cards are ready.')}
  return <div className="play-area"><h2>Match letters and sounds</h2><div className="memory-grid">{deck.map(card=>{const shown=open.some(x=>x.id===card.id)||matched.includes(card.pairId);return <button key={card.id} className={shown?'revealed':''} onClick={()=>flip(card)} aria-label={shown?card.label:'Hidden card'}>{shown?card.label:'?'}</button>})}</div><button className="quiet" onClick={reset}><RotateCcw size={16}/> New board</button><p className="gentle-feedback" role="status">{feedback}</p></div>
}

function CatchGame({ level, onComplete, onError }) {
  const [roundNo,setRoundNo]=useState(0), [round,setRound]=useState(()=>makeCatchRound(level.letters[0],level.letters)), [caught,setCaught]=useState(0), [feedback,setFeedback]=useState('Listen, then catch the matching letter. There is no timer.')
  const choose=index=>{if(index===round.correctIndex){const next=caught+1;setCaught(next);setFeedback('You caught it!');if(next>=6){onComplete('catch');return}const target=level.letters[(roundNo+1)%level.letters.length];setRoundNo(x=>x+1);setRound(makeCatchRound(target,level.letters))}else setFeedback('That letter makes a different sound. Listen and try again.')}
  return <div className="play-area"><div className="game-instruction"><h2>Catch /{round.target}/</h2><SoundButton letter={round.target} onError={onError}/></div><div className="catch-lanes">{round.options.map((letter,index)=><button key={`${roundNo}-${letter}`} onClick={()=>choose(index)}><span>{letter.toUpperCase()}</span><small>Key {index+1}</small></button>)}</div><div className="reward-row" aria-label={`${caught} of 6 catches`}>{Array.from({length:6},(_,i)=><Sparkles key={i} className={i<caught?'earned':''}/>)}</div><p className="gentle-feedback" role="status">{feedback}</p><div className="keyboard-catcher" onKeyDown={e=>{const i=Number(e.key)-1;if(i>=0&&i<round.options.length)choose(i)}} tabIndex="0">Keyboard: focus here and press 1–4</div></div>
}

export default function PhonicsGameSuite({ onProgress }) {
  const [game,setGame]=useState('trace'),[level,setLevel]=useState(LEVELS[0]),[audioError,setAudioError]=useState(''),[completed,setCompleted]=useState([])
  const complete=id=>{setCompleted(value=>[...new Set([...value,`${id}-${level.id}`])]);onProgress?.(id,level.id)}
  const props={level,onComplete:complete,onError:setAudioError}
  return <section className="hub-card game-suite"><div className="game-suite-head"><div><p className="eyebrow">Play with Bob</p><h1>Phonics games</h1><p>No countdowns, lost points or compulsory speed.</p></div><label>Level<select value={level.id} onChange={e=>setLevel(LEVELS.find(x=>x.id===Number(e.target.value)))}>{LEVELS.map(x=><option key={x.id} value={x.id}>{x.id}. {x.name}</option>)}</select></label></div><div className="game-tabs" role="tablist">{Object.entries(GAME_NAMES).map(([id,name])=><button role="tab" aria-selected={game===id} className={game===id?'active':''} key={id} onClick={()=>setGame(id)}>{completed.includes(`${id}-${level.id}`)?'✓ ':''}{name}</button>)}</div>{audioError&&<p className="audio-error" role="alert">Audio: {audioError}</p>}{game==='trace'&&<TraceGame {...props}/>} {game==='build'&&<BuildGame {...props}/>} {game==='memory'&&<MemoryGame {...props}/>} {game==='catch'&&<CatchGame {...props}/>}</section>
}
