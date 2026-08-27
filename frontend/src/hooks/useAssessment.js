import { useCallback, useState } from 'react'
import { uploadFiles, processSession, gradeSession } from '../api/client'


export const HIGHLIGHT_PALETTE = [
  { name: 'amber', bg: 'bg-amber-400/30', border: 'border-amber-400', dot: 'bg-amber-400', text: 'text-amber-300' },
  { name: 'sky', bg: 'bg-sky-400/30', border: 'border-sky-400', dot: 'bg-sky-400', text: 'text-sky-300' },
  { name: 'emerald', bg: 'bg-emerald-400/30', border: 'border-emerald-400', dot: 'bg-emerald-400', text: 'text-emerald-300' },
  { name: 'rose', bg: 'bg-rose-400/30', border: 'border-rose-400', dot: 'bg-rose-400', text: 'text-rose-300' },
  { name: 'violet', bg: 'bg-violet-400/30', border: 'border-violet-400', dot: 'bg-violet-400', text: 'text-violet-300' },
  { name: 'cyan', bg: 'bg-cyan-400/30', border: 'border-cyan-400', dot: 'bg-cyan-400', text: 'text-cyan-300' },
]

export function colorForIndex(i) {
  return HIGHLIGHT_PALETTE[i % HIGHLIGHT_PALETTE.length]
}

const STEPS = [
  { key: 'extracting_questions', label: 'Extracting questions from paper' },
  { key: 'running_ocr', label: 'Scanning answer sheet layout' },
  { key: 'extracting_answers', label: 'Transcribing handwritten answers' },
  { key: 'mapping', label: 'Mapping answers to questions' },
  { key: 'locating_highlights', label: 'Locating exact answer regions' },
]

export default function useAssessment() {
  const [stage, setStage] = useState('upload') // upload | processing | results | error
  const [sessionId, setSessionId] = useState(null)
  const [currentStepIndex, setCurrentStepIndex] = useState(0)
  const [result, setResult] = useState(null)
  const [grading, setGrading] = useState(null)
  const [error, setError] = useState(null)

  const runPipeline = useCallback(async (questionPaper, answerSheet) => {
    setStage('processing')
    setError(null)
    setCurrentStepIndex(0)
    try {
      const upload = await uploadFiles(questionPaper, answerSheet)
      setSessionId(upload.session_id)

      // Simulate step progression while the single /process call runs server-side
      let stepTimer = setInterval(() => {
        setCurrentStepIndex((i) => (i < STEPS.length - 1 ? i + 1 : i))
      }, 1800)

      const processed = await processSession(upload.session_id)
      clearInterval(stepTimer)
      setCurrentStepIndex(STEPS.length - 1)

      setResult(processed)
      setStage('results')
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Something went wrong.')
      setStage('error')
    }
  }, [])

  const runGrading = useCallback(async () => {
    if (!sessionId) return
    const data = await gradeSession(sessionId)
    setGrading(data)
    return data
  }, [sessionId])

  const reset = useCallback(() => {
    setStage('upload')
    setSessionId(null)
    setResult(null)
    setGrading(null)
    setError(null)
    setCurrentStepIndex(0)
  }, [])

  return {
    stage, sessionId, result, grading, error,
    steps: STEPS, currentStepIndex,
    runPipeline, runGrading, reset,
  }
}