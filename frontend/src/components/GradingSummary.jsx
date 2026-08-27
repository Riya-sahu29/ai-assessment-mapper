export default function GradingSummary({ grading, onGrade, grading_loading, questions }) {
  if (!grading) {
    return (
      <button
        onClick={onGrade}
        disabled={grading_loading}
        className="w-full py-2.5 rounded-lg bg-emerald-500/15 text-emerald-300 border border-emerald-500/30 hover:bg-emerald-500/25 transition text-sm font-medium disabled:opacity-50"
      >
        {grading_loading ? 'Grading…' : 'Run AI grading & feedback'}
      </button>
    )
  }

  const qById = Object.fromEntries(questions.map((q) => [q.id, q]))

  return (
    <div className="space-y-3">
      <div className="rounded-lg bg-slate-800/50 border border-slate-700 p-3">
        <p className="text-sm font-medium text-slate-100">{grading.summary}</p>
      </div>
      <div className="space-y-2 max-h-72 overflow-y-auto pr-1">
        {grading.results.map((r) => (
          <div key={r.question_id} className="rounded-lg border border-slate-800 p-2.5">
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="font-medium text-slate-300">{qById[r.question_id]?.number || r.question_id}</span>
              {r.marks_awarded != null && (
                <span className={`font-medium ${r.correct ? 'text-emerald-400' : 'text-amber-400'}`}>
                  {r.marks_awarded}/{r.marks_total}
                </span>
              )}
            </div>
            <p className="text-xs text-slate-500">{r.feedback}</p>
          </div>
        ))}
      </div>
    </div>
  )
}