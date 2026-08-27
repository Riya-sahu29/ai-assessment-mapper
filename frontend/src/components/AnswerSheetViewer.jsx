import { useEffect, useState } from 'react'
import { getAnswerPage } from '../api/client'
import HighlightOverlay from './HighlightOverlay'

export default function AnswerSheetViewer({ sessionId, activePage, setActivePage, totalPages, activeBoxes, colorClass }) {
  const [imageData, setImageData] = useState(null)

  useEffect(() => {
    let cancelled = false
    getAnswerPage(sessionId, activePage).then((data) => {
      if (!cancelled) setImageData(data)
    })
    return () => { cancelled = true }
  }, [sessionId, activePage])

  const boxesForPage = (activeBoxes || []).filter((b) => b.page === activePage)

  return (
    <div>
      {totalPages > 1 && (
        <div className="flex gap-1 mb-3">
          {Array.from({ length: totalPages }).map((_, i) => (
            <button
              key={i}
              onClick={() => setActivePage(i)}
              className={`text-xs px-2.5 py-1 rounded-md border transition
                ${activePage === i ? 'border-indigo-400 text-indigo-300 bg-indigo-500/10' : 'border-slate-800 text-slate-500 hover:border-slate-700'}`}
            >
              Page {i + 1}
            </button>
          ))}
        </div>
      )}

      <div className="relative rounded-lg overflow-hidden border border-slate-800 bg-slate-900">
        {imageData ? (
          <>
            <img
              src={`data:image/png;base64,${imageData.image_b64}`}
              alt={`Answer sheet page ${activePage + 1}`}
              className="w-full h-auto block"
            />
            {boxesForPage.map((box, i) => (
              <HighlightOverlay key={i} box={box} colorClass={colorClass} />
            ))}
          </>
        ) : (
          <div className="aspect-[3/4] flex items-center justify-center text-slate-600 text-sm">Loading page…</div>
        )}
      </div>
    </div>
  )
}