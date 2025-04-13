// import axios from 'axios'

// const apiClient = axios.create({
//   baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', // Point to gateway, ensure scheme is present
//   withCredentials: true, // Important for sending/receiving cookies
//   headers: {
//     Accept: 'application/json',
//     'Content-Type': 'application/json'
//   }
// })


export default {
  getDigests() {
    return Promise.resolve({
      data: {
        items: [
          {
            id: 1,
            start_datetime: "2024-03-22T00:00:00",
            title: "Could Digital Currencies Lead to the Disappearance of Cash?",
            summary: "Исследование анализирует влияние цифровых валют центральных банков на спрос на наличные деньги, подчеркивая потенциальное вытеснение физической валюты и связанные с этим последствия для денежно-кредитной политики.",
            keywords: ["Цифровые валюты", "двусторонняя модель рынка", "платежные системы", "изчезновение наличных", "деньги"],
            s3_url: "/test_data/digests/Could Digital Currencies Lead to the Disappearance_20250322_131047.pdf"
          },
          {
            id: 2,
            start_datetime: "2024-03-22T00:00:00",
            title: "Lost Generations? Fertility and Economic Growth in Europe",
            summary: "Снижение рождаемости оказывает значительное влияние на рост ВВП на душу населения. В работе используется инструментальный подход для анализа связи между рождаемостью и экономическим ростом в 42 странах Европы.",
            keywords: ["Рождаемость", "экономический рост", "инструментальная переменная", "двухступенчатые наименьшие квадраты", "старение населения"],
            s3_url: "/test_data/digests/Lost Generations Fertility and Economic Growth in _20250322_131145.pdf"
          },
          {
            id: 3,
            start_datetime: "2024-03-22T00:00:00",
            title: "The Insurer Channel of Monetary Policy",
            summary: "Анализируется роль страховых компаний в передаче эффектов монетарной политики через изменение их инвестиционного поведения, особенно в отношении рискованных облигаций и премий за риск.",
            keywords: ["Монетарная политика", "страховые компании", "риск-премии", "инвестиционное поведение", "долговые ценные бумаги"],
            s3_url: "/test_data/digests/The Insurer Channel of Monetary Policy_20250322_031750.pdf"
          }
        ]
      }
    });
  },
  downloadDigest(url) {
    return fetch(url)
      .then(res => {
        if (!res.ok) throw new Error('Ошибка загрузки PDF')
        return res.blob()
      })
      .then(blob => ({ data: blob }))
  },
  getArticles() {
    return Promise.resolve({
      data: [
        {
          title: "A Robust Asymptotic Control Model to Analyze Climate Policy with CDR Options",
          file_path: "/test_data/articles/ssrn-5056227.pdf",
          section: "Climate policy",
          published_date: "2024-12-20T00:00:00"
        },
        {
          title: "The Effects of Climate Policies on U.S. Listed Energy Firm Returns: Evidence from Iija, Chips, and Ira",
          file_path: "/test_data/articles/ssrn-5044524.pdf",
          section: "Climate policy",
          published_date: "2024-12-17T00:00:00"
        },
        {
          title: "Weekly Inflation Forecasting: A Two-Step Machine Learning Methodology",
          file_path: "/test_data/articles/ssrn-5001681.pdf",
          section: "Inflation",
          published_date: "2024-12-19T00:00:00"
        }
      ]
    });
  },
  getActual() {
    return Promise.resolve({
      data: {
        items: [
          {
            id: 1,
            title: "Банк России: мониторинг отраслевых финансовых потоков - рост деловой активности продолжается",
            body: "В марте объем финансовых поступлений, проведенных через Банк России, оказался близок к февральскому значению и на 8,2% выше среднего уровня IV квартала 2024 года. Без учета добывающих отраслей, производства нефтепродуктов и государственного управления входящие платежи увеличились на 17,1%, в то время как в среднем за I квартал рост составил 14,8%."
          },
          {
            id: 2,
            title: "ECB Consumer Expectations Survey results – February 2025",
            body: "Median consumer perceptions of inflation over the previous 12 months decreased, while median inflation expectations for the next 12 months and for three years ahead remained unchanged. Expectations for nominal income growth over the next 12 months increased, while expectations for spending growth over the next 12 months decreased."
          },
          {
            id: 3,
            title: "ECB launches pilot project for research access to confidential statistical data",
            body: "Anonymised data on individual banks in the entire euro area will be available to academic researchers. Several access modes will be tested with a view to establishing a permanent framework for research access to ECB data."
          }
        ]
      }
    });
  },
};
//     // Article endpoints
//     getArticles(skip = 0, limit = 10) {
//       // Добавляем префикс /api/v1/
//       return apiClient.get('/api/v1/science/articles', {
//         params: {
//           skip,
//           limit
//         }
//       })
//     },
// };
