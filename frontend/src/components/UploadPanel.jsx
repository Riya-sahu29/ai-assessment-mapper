import { useRef, useState } from 'react'

function Dropzone({ label, hint, file, onFile, accent }) {
  const inputRef = useRef(null)
  const [dragOver, setDragOver] = useState(false)

  const handleDrop = (e) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f) onFile(f)
  }

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
      onDragLeave={() => setDragOver(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`cursor-pointer rounded-xl border-2 border-dashed p-8 text-center transition
        ${dragOver ? 'border-indigo-400 bg-indigo-500/5' : 'border-slate-700 hover:border-slate-600'}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".pdf,.png,.jpg,.jpeg,.webp"
        className="hidden"
        onChange={(e) => e.target.files?.[0] && onFile(e.target.files[0])}
      />
      <div className={`w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center ${accent}`}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <path d="M12 3v12m0-12 4 4m-4-4-4 4M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-2" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>
      <p className="font-medium text-slate-100">{label}</p>
      <p className="text-sm text-slate-500 mt-1">{hint}</p>
      {file && (
        <p className="mt-3 text-sm text-emerald-400 truncate">{file.name}</p>
      )}
    </div>
  )
}

export default function UploadPanel({ onSubmit }) {
  const [questionPaper, setQuestionPaper] = useState(null)
  const [answerSheet, setAnswerSheet] = useState(null)

  const canSubmit = questionPaper && answerSheet

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-10">
        <h1 className="text-2xl font-semibold tracking-tight">Upload question paper & answer sheet</h1>
        <p className="text-slate-400 mt-2 text-sm">
          We'll extract every question, map the student's answers, and highlight exactly where each answer sits.
        </p>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <Dropzone
          label="Question Paper"
          hint="PDF or image"
          file={questionPaper}
          onFile={setQuestionPaper}
          accent="bg-indigo-500/15 text-indigo-300"
        />
        <Dropzone
          label="Student Answer Sheet"
          hint="PDF or image, handwritten"
          file={answerSheet}
          onFile={setAnswerSheet}
          accent="bg-amber-500/15 text-amber-300"
        />
      </div>

      <button
        disabled={!canSubmit}
        onClick={() => onSubmit(questionPaper, answerSheet)}
        className={`mt-8 w-full py-3 rounded-lg font-medium transition
          ${canSubmit
            ? 'bg-indigo-500 hover:bg-indigo-400 text-slate-950'
            : 'bg-slate-800 text-slate-500 cursor-not-allowed'}`}
      >
        Start extraction
      </button>
    </div>
  )
}