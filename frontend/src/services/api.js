import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  withCredentials: false,
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})

export default {
  // News endpoints
  getNews(skip = 0, limit = 10) {
    return apiClient.get('/api/v1/news/', {
      params: {
        skip,
        limit
      }
    })
  },

  // Digests endpoints
  getDigests(skip = 0, limit = 20) {
    return apiClient.get('/api/v1/digests/', {
      params: {
        skip,
        limit
      }
    })
  },

  downloadDigest(id) {
    return apiClient.get(`/api/v1/digests/download/${id}`, {
      responseType: 'blob' // Important for file downloads
    })
  }
}
