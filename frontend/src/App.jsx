import UploadPanel from './components/UploadPanel'
import ProcessingProgress from './components/ProcessingProgress'
import ResultsView from './components/ResultsView'
import useAssessment from './hooks/useAssessment'

export default function App() {
  const assessment = useAssessment()
  const { stage, error, reset } = assessment

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-indigo-500 flex items-center justify-center font-bold text-slate-950">A</div>
          <span className="font-semibold tracking-tight">AI Assessment Mapper</span>
        </div>
        {stage !== 'upload' && (
          <button
            onClick={reset}
            className="text-sm text-slate-400 hover:text-slate-100 border border-slate-700 rounded-md px-3 py-1.5 transition"
          >
            Start new assessment
          </button>
        )}
      </header>

      <main className="max-w-6xl mx-auto px-6 py-10">
        {stage === 'upload' && <UploadPanel onSubmit={assessment.runPipeline} />}
        {stage === 'processing' && (
          <ProcessingProgress steps={assessment.steps} currentStepIndex={assessment.currentStepIndex} />
        )}
        {stage === 'results' && <ResultsView assessment={assessment} />}
        {stage === 'error' && (
          <div className="max-w-lg mx-auto text-center py-20">
            <p className="text-rose-400 font-medium mb-2">Processing failed</p>
            <p className="text-slate-400 text-sm mb-6">{error}</p>
            <button
              onClick={reset}
              className="bg-indigo-500 hover:bg-indigo-400 text-slate-950 font-medium px-4 py-2 rounded-md transition"
            >
              Try again
            </button>
          </div>
        )}
      </main>
    </div>
  )
}