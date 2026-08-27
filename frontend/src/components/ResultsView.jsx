import { useState } from 'react'
import QuestionList from './QuestionList'
import AnswerSheetViewer from './AnswerSheetViewer'
import GradingSummary from './GradingSummary'
import { colorForIndex } from '../hooks/useAssessment'

export default function ResultsView({ assessment }) {
  const { sessionId, result, grading, runGrading } = assessment
  const { questions, mappings, unmatched_blocks, answer_blocks } = result

  const [activeId, setActiveId] = useState(questions[0]?.id || null)
  const [activePage, setActivePage] = useState(0)
  const [gradingLoading, setGradingLoading] = useState(false)

  const activeIndex = questions.findIndex((q) => q.id === activeId)
  const activeMapping = mappings.find((m) => m.question_id === activeId)
  const colorClass = colorForIndex(activeIndex >= 0 ? activeIndex : 0)

  const totalPages = Math.max(
    1,
    ...answer_blocks.map((b) => b.page + 1),
  )

  const handleSelect = (id) => {
    setActiveId(id)
    const mapping = mappings.find((m) => m.question_id === id)
    const firstBox = mapping?.highlight_boxes?.[0]
    if (firstBox) setActivePage(firstBox.page)
  }

  const handleGrade = async () => {
    setGradingLoading(true)
    try {
      await runGrading()
    } finally {
      setGradingLoading(false)
    }
  }

  const unmatched = unmatched_blocks
    .map((id) => answer_blocks.find((b) => b.id === id))
    .filter(Boolean)

  return (
    <div className="grid lg:grid-cols-[320px_1fr_280px] gap-6">
      <div>
        <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">
          Questions ({questions.length})
        </h2>
        <QuestionList
          questions={questions}
          mappings={mappings}
          activeId={activeId}
          onSelect={handleSelect}
        />

        {unmatched.length > 0 && (
          <div className="mt-6">
            <h3 className="text-xs font-semibold text-rose-400 mb-2 uppercase tracking-wide">
              Unmatched content ({unmatched.length})
            </h3>
            <div className="space-y-2">
              {unmatched.map((b) => (
                <div key={b.id} className="rounded-lg border border-rose-500/20 bg-rose-500/5 p-2.5">
                  <p className="text-[11px] text-slate-500 mb-1">Page {b.page + 1}</p>
                  <p className="text-xs text-slate-400 line-clamp-3">{b.raw_text}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">Answer Sheet</h2>
        <AnswerSheetViewer
          sessionId={sessionId}
          activePage={activePage}
          setActivePage={setActivePage}
          totalPages={totalPages}
          activeBoxes={activeMapping?.highlight_boxes}
          colorClass={colorClass}
        />
        {!activeMapping?.located && activeMapping?.status === 'answered' && (
          <p className="text-xs text-amber-400 mt-2">
            Answer found but exact region couldn't be confidently located on the page.
          </p>
        )}
      </div>

      <div>
        <h2 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wide">Grading</h2>
        <GradingSummary
          grading={grading}
          onGrade={handleGrade}
          grading_loading={gradingLoading}
          questions={questions}
        />
      </div>
    </div>
  )
}