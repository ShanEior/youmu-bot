import axios from 'axios'

const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api',
})

export function healthCheck() {
  return apiClient.get('/health')
}

export function uploadFile(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiClient.post('/files/upload', formData)
}

export function convertFile(fileId) {
  return apiClient.post('/files/convert', { file_id: fileId })
}

export function downloadFile(outputFileId) {
  return apiClient.get(`/files/download/${outputFileId}`)
}
