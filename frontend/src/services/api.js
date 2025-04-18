import axios from 'axios'

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000', // Point to gateway, ensure scheme is present
  withCredentials: true, // Important for sending/receiving cookies
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json'
  }
})


export default {
  getDigests() {
    return Promise.resolve({
      data: {
        items: [
          {
            id: 1,
            start_datetime: "2025-03-22T00:00:00",
            title: "Could Digital Currencies Lead to the Disappearance of Cash from the Market? Insights from a “Merchant-Customer” Model",
            summary: "Исследование показывает, что масштабное внедрение цифровых валют может сместить равновесие платёжной системы и привести к вытеснению наличных денег. Авторы предлагают аналитическую модель двухстороннего рынка, демонстрирующую влияние фиксированных и переменных издержек, сетевых эффектов и предпочтений участников. Выводы подчёркивают важность регуляторных мер, обеспечивающих баланс между инновациями и сохранением наличных как элемента финансовой устойчивости.",
            keywords: ["Цифровые валюты", "двусторонний рынок", "платежная система", "денежно-кредитная политика", "финансовая стабильность", "цифровой рубль"],
            s3_url: "/test_data/digests/Could_Digital_Currencies_Disappearance_Market_Merchant_Model_20250322.pdf"
          },
          {
            id: 2,
            start_datetime: "2025-03-22T00:00:00",
            title: "Lost Generations? Fertility and Economic Growth in Europe",
            summary: "Исследование посвящено влиянию ультра-низкой рождаемости на экономический рост в Европе. Используя панельные данные по 42 странам за период 1960–2022 годов и инструментальную переменную (сравнительный индекс абортов), автор выявляет положительное влияние рождаемости на ВВП на душу населения. На примере Литвы показано, что при сохранении низкой рождаемости доходы могут снизиться на 17,6%, что подчёркивает необходимость демографических и экономических реформ.",
            keywords: ["Демографические тенденции", "экономический рост", "Европа"],
            s3_url: "/test_data/digests/Lost_Generations_Fertility_Economic_Growth_Europe_20250322.pdf"
          },
          {
            id: 3,
            start_datetime: "2025-03-22T00:00:00",
            title: "The Insurer Channel of Monetary Policy",
            summary: "Исследование анализирует роль страховых компаний в передаче монетарной политики через долговой рынок. Авторы исследуют, как изменения долгосрочных безрисковых ставок влияют на инвестиционное поведение компаний с длительными обязательствами. Используя высокочастотные транзакционные данные и учёт регуляторных реформ, показано, что увеличение спрэда между доходностями корпоративных облигаций и 30-летних казначейских бумаг меняет спрос на частный долг. Результаты подчёркивают значение специфики страхового сектора при разработке монетарной политики.",
            keywords: ["Монетарная политика", "риск-премии", "долговой рынок"],
            s3_url: "/test_data/digests/The_Insurer_Channel_of_Monetary_Policy_20250322.pdf"
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
  getArticles(skip = 0, limit = 10) {
    return apiClient.get('/api/v1/science/articles', {
      params: {
        skip,
        limit
      }
    })
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
