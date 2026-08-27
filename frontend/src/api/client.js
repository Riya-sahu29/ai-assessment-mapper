import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const client = axios.create({ baseURL: API_BASE })

export async function uploadFiles(questionPaper, answerSheet) {
  const form = new FormData()
  form.append('question_paper', questionPaper)
  form.append('answer_sheet', answerSheet)
  const { data } = await client.post('/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function processSession(sessionId) {
  const { data } = await client.post(`/process/${sessionId}`)
  return data
}

export async function getStatus(sessionId) {
  const { data } = await client.get(`/status/${sessionId}`)
  return data
}

export async function getAnswerPage(sessionId, pageIndex) {
  const { data } = await client.get(`/session/${sessionId}/page/answer/${pageIndex}`)
  return data
}

export async function gradeSession(sessionId) {
  const { data } = await client.post(`/grade/${sessionId}`)
  return data
}

export default client