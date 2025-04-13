    <template>
    <div class="articles-container">
        <!-- Left column for digests (3/4 width) -->
        <div class="left-column">
        <h2 class="section-heading">Дайджесты экономических исследований</h2>
        <div v-if="digestsLoading" class="loading">Загрузка дайджестов...</div>
        <div v-else-if="digestsError" class="error">{{ digestsError }}</div>
        <div v-else>
            <div v-for="digest in formattedDigests" :key="digest.id" class="digest-item">
            <h3 class="digest-title">{{ digest.displayTitle }}</h3>
            <div class="digest-body">
            <strong>Резюме.</strong> {{ digest.summary }}
            <template v-if="digest.keywords && digest.keywords.length">
                <div class="keywords-line">
                <strong>Ключевые слова.</strong><br>
                {{ digest.keywords.join(', ') }}
                </div>
            </template>
            </div>

            <button class="download-btn" @click="downloadDigest(digest.s3_url)">
                Скачать PDF
            </button>
            </div>
        </div>

        <!-- ВНИМАНИЕ: добавляем сюда статьи, не внутрь предыдущего блока -->
        <h2 class="section-heading">Научные статьи</h2>
        <div v-if="articlesLoading" class="loading">Загрузка статей...</div>
        <div v-else-if="articlesError" class="error">{{ articlesError }}</div>
        <div v-else>
            <div v-for="(articlesGroup, section) in groupedArticles" :key="section">
            <h3 class="section-subheading">{{ section }}</h3>
            <div v-for="article in articlesGroup" :key="article.title + article.published_date" class="digest-item">
                <h4 class="digest-title">{{ article.title }}</h4>
                <div class="digest-body">
                Опубликовано: {{ new Date(article.published_date).toLocaleDateString("ru-RU") }}
                </div>
                <button class="download-btn" @click="downloadDigest(article.file_path)">
                Скачать PDF 
                </button>
            </div>
            </div>
        </div>
        </div>

        <!-- Right column -->
        <div class="right-column">
        <h2 class="section-heading">Актуальное</h2>

        <template v-if="formattedDigests.length">
            <div
            v-for="digest in formattedDigests.slice(0, 2)"
            :key="digest.id"
            class="digest-item"
            >
            <h4 class="digest-title">{{ digest.displayTitle }}</h4>
            <div class="digest-body">
                <strong>Резюме.</strong> {{ digest.summary }}
                <template v-if="digest.keywords && digest.keywords.length">
                <div class="keywords-line">
                    <strong>Ключевые слова.</strong>
                    <div>{{ digest.keywords.join(', ') }}</div>
                </div>
                </template>
            </div>
            </div>
        </template>

        <template v-else>
            <p>Скоро здесь появятся материалы...</p>
        </template>
        </div>
    </div> 
    </template>
    
    <script>
    import api from '@/services/api'

    export default {
    data() {
        return {
        digests: [],
        digestsLoading: true,
        digestsError: null,
        articles: [],
        articlesLoading: true,
        articlesError: null,
        }
    },
    async created() {
        await Promise.all([
        this.fetchDigests(),
        this.fetchArticles()
    ])
    },
    computed: {
    formattedDigests() {
        return this.digests.map((digest, index) => {
        const date = new Date(digest.start_datetime)
        const formattedDate = date.toLocaleDateString('ru-RU')
        return {
            ...digest,
            displayTitle: `№ ${String(index + 1).padStart(3, '0')} (${formattedDate}): ${digest.title}`
        }
        })
    },
    groupedArticles() {
        // Группировка по section
        const groups = {}
        this.articles.forEach(article => {
        if (!groups[article.section]) {
            groups[article.section] = []
        }
        groups[article.section].push(article)
        })
        return groups
    }
    },
    methods: {
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
        async downloadDigest(url) {
        try {
            const response = await api.downloadDigest(url)
            const blobUrl = window.URL.createObjectURL(response.data)
            const link = document.createElement('a')
            link.href = blobUrl
            link.setAttribute('download', url.split('/').pop())
            document.body.appendChild(link)
            link.click()
            link.remove()
        } catch (error) {
            console.error('Ошибка загрузки PDF:', error)
        }
        },
        async fetchArticles() {
        try {
            const response = await api.getArticles()
            this.articles = response.data
        } catch (err) {
            this.articlesError = err.message || 'Ошибка загрузки статей'
        } finally {
            this.articlesLoading = false
        }
        }
    }
    }
    </script>

    <style scoped>
    .articles-container {
    display: flex;
    gap: 20px;
    padding: 20px;
    max-width: 1700px;
    margin: 0 auto;
    }

    .section-heading {
    font-size: 30px;
    margin-top: 20px;
    margin-bottom: 20px;
    border-bottom: 2px solid #003367;
    padding-bottom: 15px;
    color: #003367;
    }

    .section-heading-2 {
    font-size: 20px;
    margin-top: 65px;
    border-bottom: 2px solid #003367;
    padding-bottom: 5px;
    color: #003367;
    }

    .section-subheading {
    font-size: 20px;
    margin-top: 40px;
    padding: 6px 12px;
    background-color: #f2f6fa;
    border-left: 4px solid #003367;
    color: #003367;
    font-weight: 600;
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
    font-size: 18px;
    font-weight: 500;
    color: #222;
    margin-bottom: 20px;
    }

    .digest-body {
    font-size: 18px;
    line-height: 1.5;
    color: #555;
    margin-bottom: 15px;
    }

    .digest-item {
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 1px dashed #ccc;
    }

    .keywords-list {
    margin: 10px 0;
    padding-left: 0;
    list-style: none;
    }

    .keywords-list li {
    position: relative;
    padding-left: 18px;
    margin-bottom: 4px;
    }

    .keywords-list li::before {
    content: "•";
    position: absolute;
    left: 0;
    top: 0;
    color: #003367;
    font-size: 18px;
    line-height: 1.4;
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
    padding: 20px;
    }

    .loading {
    color: #666;
    font-style: italic;
    }
    </style>
