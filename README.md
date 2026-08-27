# AI Assessment Mapper

AI-powered tool that automatically maps handwritten student answer sheets to their corresponding question papers, transcribes the handwriting, matches each answer to the right question, and grades the results — with visual highlighting of exactly where each answer appears on the scanned sheet.

---

## ✨ Features

- **Dual-file upload** — upload a question paper and an answer sheet (PDF or image), with live processing progress.
- **Ordered question extraction** — extracts every question from the question paper in the exact order printed, including labelled sub-parts (e.g. `11 (a)`, `11 (b)`) as separate entries with original numbering preserved.
- **Handwriting transcription** — uses a vision-language model to transcribe handwritten answers into text, split into logical answer blocks.
- **Robust answer-to-question mapping**
  - Deterministic exact-number matching (e.g. `Ans 10` → Question 10) for high-confidence pairing.
  - LLM-based content reasoning as a fallback for unlabeled or ambiguous answers.
  - Correctly handles answers written out of order, unanswered questions, and content that matches no question (surfaced separately as "unmatched content").
  - Supports answers that span multiple blocks or pages.
- **Visual answer highlighting** — locates and highlights the exact region of each matched answer on the original scanned answer sheet, using OCR word-box coordinates.
- **AI-assisted grading** — evaluates each answered question and returns a score with feedback.

---

## 🏗️ Architecture

```
frontend/               React + Vite single-page app
  src/
    components/
      UploadPanel.jsx        File upload UI
      ProcessingProgress.jsx Live processing status
      ResultsView.jsx        Questions / answer sheet / grading layout
      QuestionList.jsx       Question list with status badges
      AnswerSheetViewer.jsx  Renders the scanned answer sheet + highlights
      HighlightOverlay.jsx   Positions a highlight box (from % coordinates)
      GradingSummary.jsx     Displays AI grading results
    hooks/
      useAssessment.js       Core pipeline state (upload → process → grade)
    api/
      client.js               API calls to the backend

backend/                 FastAPI application
  app/
    routers/
      process.py             /upload, /process, /status, page-image endpoints
    services/
      pdf_utils.py            PDF/image → page images, base64 encoding
      ocr_service.py          Tesseract OCR word-box extraction
      ai_extraction.py        Vision-model question/answer extraction (Groq)
      mapping_service.py      Answer-to-question mapping (deterministic + LLM)
      highlight_service.py    Locates answer regions on the page (bounding boxes)
    models/
      schemas.py               Pydantic response models
    storage.py                 In-memory session storage
    config.py                  Environment/config settings
```

### Processing pipeline

1. **Upload** — question paper and answer sheet are uploaded and converted to page images.
2. **Extract questions** — a vision model reads the question paper and extracts every question, preserving numbering and sub-parts.
3. **OCR the answer sheet** — Tesseract extracts word-level bounding boxes for later highlighting.
4. **Transcribe answers** — a vision model transcribes the handwritten answer sheet into discrete answer blocks.
5. **Map answers to questions** — exact-number matches are paired deterministically; remaining blocks are resolved via LLM reasoning. Unmatched content is flagged separately.
6. **Locate highlights** — each mapped answer block is located within the page's OCR word boxes and converted into percentage-based bounding box coordinates.
7. **Grade** — questions with matched answers are evaluated and scored, with feedback per question.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- FastAPI
- [Poppler](https://github.com/oschwartz10612/poppler-windows) (for PDF-to-image conversion)
- [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (for word-box extraction)
- A [Groq API key](https://console.groq.com)

### Backend setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

Create a `.env` file in `backend/`:

```env
GROQ_API_KEY=your_groq_api_key
VISION_MODEL=qwen/qwen3.6-27b
TEXT_MODEL=your_text_model
```

Run the server:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The app will be available at `http://localhost:5173`.

---

## 📡 API Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/upload` | Upload question paper + answer sheet files |
| `POST` | `/process/{session_id}` | Run the full extraction, mapping, and highlighting pipeline |
| `GET`  | `/status/{session_id}` | Poll processing status |
| `GET`  | `/session/{session_id}/page/answer/{page_index}` | Fetch a specific answer sheet page image |
| `POST` | `/grade/{session_id}` | Run AI grading on the processed session |

---

## 🛠️ Tech Stack

**Backend:** FastAPI, Groq (vision + text models), pdf2image (Poppler), Pillow, pytesseract, rapidfuzz

**Frontend:** React, Vite, Tailwind CSS

---

## 📌 Notes

- Sessions are currently stored in memory; restarting the backend clears all active sessions.
- Vision model requests are size-limited by the provider's token-per-minute rate limits — page images are resized and compressed before being sent to keep requests within limits.

---

## 📄 License

This project is provided as-is for educational/assessment purposes.
