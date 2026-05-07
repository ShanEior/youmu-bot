import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://127.0.0.1:5000',
})

export function healthCheck() {
  return apiClient.get('/api/health')
}

export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)

  return apiClient.post('/api/files/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

export function convertFile(fileId) {
  return apiClient.post('/api/files/convert', { file_id: fileId })
}

export function downloadFile(outputFileId) {
  return apiClient.get(`/api/files/download/${outputFileId}`, {
    responseType: 'blob',
  })
}
