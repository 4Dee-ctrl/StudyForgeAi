import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000',
  timeout: 120000,
  headers: {
    'Content-Type': 'application/json',
  },
})

function getErrorMessage(error) {
  if (!error.response) {
    return 'Unable to connect to the server. Make sure the backend is running.'
  }

  const detail = error.response.data?.detail
  if (detail) return detail

  const messages = {
    413: 'File is too large. Maximum size is 10 MB.',
    415: 'Unsupported file type. Please upload a PDF or PPTX file.',
    422: 'The request is invalid. Check the input and try again.',
    429: 'Rate limit exceeded. Please wait a moment and try again.',
    500: 'Server error. Please try again later.',
  }

  return messages[error.response.status] || 'Something went wrong. Please try again.'
}

client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const enhanced = new Error(getErrorMessage(error))
    enhanced.status = error.response?.status
    enhanced.data = error.response?.data
    return Promise.reject(enhanced)
  },
)

export async function healthCheck() {
  return client.get('/api/health')
}

export async function extractFile(file) {
  const form = new FormData()
  form.append('file', file)

  return client.post('/api/extract', form, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export async function generateStudyAid(text, type) {
  return client.post('/api/generate', { text, type })
}

export async function exportStudyAid(content, format, title) {
  const response = await axios.post(
    `${client.defaults.baseURL}/api/export`,
    { content, format, title },
    {
      responseType: 'blob',
      timeout: 120000,
      headers: {
        'Content-Type': 'application/json',
      },
    },
  )

  return response
}
