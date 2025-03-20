<template>
  <div class="news-container">
    <!-- Left column for digests (3/4 width) -->
    <div class="left-column">
      <h2>Дайджесты</h2>
      <div v-if="digestsLoading" class="loading">Загрузка дайджестов...</div>
      <div v-else-if="digestsError" class="error">{{ digestsError }}</div>
      <div v-else>
        <div v-for="digest in digests" :key="digest.id" class="digest-item">
          <h3 class="digest-title">{{ digest.title }}</h3>
          <div class="digest-body">{{ digest.body }}</div>
          <button class="download-btn" @click="downloadDigest(digest.id)">
            Скачать PDF
          </button>
        </div>
      </div>
    </div>

    <!-- Right column for recent news (1/4 width) -->
    <div class="right-column">
      <h2>Актуальное</h2>
      <div v-if="loading" class="loading">Загрузка...</div>
      <div v-else>
        <div v-for="item in news" :key="item.id" class="news-item">
          <div class="news-source">{{ item.source_name }}</div>
          <div class="news-title">{{ item.title }}</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api'

export default {
  data() {
    return {
      news: [],
      digests: [],
      loading: true,
      error: null,
      digestsLoading: true,
      digestsError: null
    }
  },
  async created() {
    await Promise.all([
      this.fetchNews(),
      this.fetchDigests()
    ])
  },
  methods: {
    async fetchNews() {
      try {
        const response = await api.getNews()
        this.news = response.data
      } catch (err) {
        this.error = err.message || 'Ошибка загрузки новостей'
      } finally {
        this.loading = false
      }
    },
    async fetchDigests() {
      try {
        const response = await api.getDigests()
        this.digests = response.data.items
      } catch (err) {
        this.digestsError = err.message || 'Ошибка загрузки дайджестов'
      } finally {
        this.digestsLoading = false
      }
    },
    async downloadDigest(id) {
      try {
        const response = await api.downloadDigest(id)
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.setAttribute('download', `digest_${id}.pdf`)
        document.body.appendChild(link)
        link.click()
        link.remove()
      } catch (error) {
        console.error('Download failed:', error)
      }
    }
  }
}
</script>

<style scoped>
.news-container {
  display: flex;
  gap: 20px;
  padding: 20px;
}

.left-column {
  flex: 3;
  padding: 20px;
}

.digest-item {
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.digest-title {
  font-size: 20px;
  font-weight: bold;
  margin-bottom: 10px;
  color: #333;
}

.digest-body {
  font-size: 16px;
  line-height: 1.5;
  color: #555;
  margin-bottom: 15px;
}

.download-btn {
  background-color: #003367;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background-color 0.2s;
}

.download-btn:hover {
  background-color: #002142;
}

.error {
  color: #dc3545;
  font-style: italic;
}

.right-column {
  flex: 1;
}

.news-item {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.news-source {
  font-size: 14px;
  color: #666;
  margin-bottom: 5px;
}

.news-title {
  font-size: 16px;
  font-weight: 500;
  line-height: 1.3;
}

.loading {
  color: #666;
  font-style: italic;
}
</style>
