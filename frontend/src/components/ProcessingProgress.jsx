export default function ProcessingProgress({ steps, currentStepIndex }) {
  return (
    <div className="max-w-lg mx-auto py-16">
      <div className="text-center mb-10">
        <div className="w-14 h-14 mx-auto rounded-full border-2 border-indigo-400 border-t-transparent animate-spin mb-4" />
        <h2 className="text-lg font-semibold">Processing the assessment</h2>
        <p className="text-slate-400 text-sm mt-1">This usually takes under a minute.</p>
      </div>

      <ol className="space-y-3">
        {steps.map((step, i) => {
          const done = i < currentStepIndex
          const active = i === currentStepIndex
          return (
            <li key={step.key} className="flex items-center gap-3">
              <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs flex-shrink-0
                ${done ? 'bg-emerald-500 text-slate-950' : active ? 'bg-indigo-500 text-slate-950' : 'bg-slate-800 text-slate-500'}`}>
                {done ? '✓' : i + 1}
              </div>
              <span className={`text-sm ${active ? 'text-slate-100' : done ? 'text-slate-400' : 'text-slate-600'}`}>
                {step.label}
              </span>
            </li>
          )
        })}
      </ol>
    </div>
  )
}