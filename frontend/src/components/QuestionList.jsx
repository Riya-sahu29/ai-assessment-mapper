import { colorForIndex } from '../hooks/useAssessment'

const STATUS_LABEL = {
  answered: 'Answered',
  unanswered: 'Unanswered',
  unmatched: 'Unmatched',
}

export default function QuestionList({ questions, mappings, activeId, onSelect }) {
  const mappingByQ = Object.fromEntries(mappings.map((m) => [m.question_id, m]))

  return (
    <div className="space-y-2">
      {questions.map((q, i) => {
        const mapping = mappingByQ[q.id]
        const color = colorForIndex(i)
        const status = mapping?.status || 'unanswered'
        const isActive = activeId === q.id

        return (
          <button
            key={q.id}
            onClick={() => onSelect(q.id)}
            className={`w-full text-left rounded-lg border p-3 transition
              ${isActive ? `${color.border} bg-slate-800/60` : 'border-slate-800 hover:border-slate-700 bg-slate-900/40'}`}
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex items-center gap-2">
                <span className={`w-2.5 h-2.5 rounded-full ${color.dot}`} />
                <span className="font-medium text-sm text-slate-100">{q.number}</span>
              </div>
              <span className={`text-[11px] px-2 py-0.5 rounded-full font-medium
                ${status === 'answered' ? 'bg-emerald-500/15 text-emerald-300' :
                  status === 'unanswered' ? 'bg-slate-700/50 text-slate-400' :
                  'bg-rose-500/15 text-rose-300'}`}>
                {STATUS_LABEL[status]}
              </span>
            </div>
            <p className="text-xs text-slate-500 mt-1.5 line-clamp-2">{q.text}</p>
          </button>
        )
      })}
    </div>
  )
}