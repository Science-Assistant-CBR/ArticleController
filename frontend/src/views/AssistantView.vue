<template>
  <div class="flex p-5 bg-white text-black font-sans" style="width: 100%">
    <!-- Левая боковая панель (навигация) -->
    <aside class="w-1/5 pr-4 border-r border-gray-300">
      <div class="mb-8">
        <h3 class="text-lg font-semibold mb-2">Проекты</h3>
        <ul class="space-y-1">
          <li>Экономика</li>
          <li>ИИ в бизнесе</li>
          <li>Санкции</li>
          <li>Еще...</li>
        </ul>
      </div>
      <div>
        <h3 class="text-lg font-semibold mb-2">История</h3>
        <ul class="space-y-1">
          <li>Чат 1</li>
          <li>Чат 2</li>
          <li>Чат 3</li>
        </ul>
      </div>
    </aside>

    <!-- Основное содержимое -->
    <main class="flex flex-col flex-1 px-5">
      <div v-for="message in assistant.chat.history" :class='message.sender == "user" ? "self-end" : "self-start"' class="w-4/5 bg-gray-100 p-4 rounded-lg mb-6">
        <h2 class="text-xl font-bold text-balance">
          {{ message.text }}
        </h2>
      </div>
      <div style="flex-grow: 1; height: 100%"></div>
      <div>
        <form @submit.prevent="sendChatMessage">
          <input v-model="chatMessage" type="text" placeholder="Задайте вопрос..."
            class="w-full p-3 border border-gray-300 rounded-lg bg-gray-100 focus:outline-none focus:ring-2 focus:ring-blue-500" :disabled="assistant.chat.disabled"/>
          <input type="submit" class="hidden" />
        </form>
      </div>
    </main>

    <!-- Правая боковая панель (источники) -->
    <aside v-if="assistant.sources.visible" class="w-1/5 pl-4 border-l border-gray-300">
      <h3 class="text-lg font-semibold mb-4">Источники</h3>
      <ol v-for="source in assistant.sources.items" class="list-decimal list-inside space-y-4">
        <li>
          {{ source }}
        </li>
      </ol>
    </aside>
  </div>
</template>

<script>
export default {
  name: 'StaticPage',
  data() {
    return {
      assistant: {
        chat: {
          disabled: false,
          history: []
        },
        sources: {
          items: [],
          visible: false
        }
      }
    }
  },
  methods: {
    sendChatMessage(event) {
      this.assistant.chat.disabled = true;
      this.assistant.chat.history.push({
        sender: "user",
        text: this.chatMessage
      })

      var sharedState = this;
      // Get the LLM response
      axios.post("/api/v1/vectors/science", {
          query_text: this.chatMessage
      }).then(function(response) {
        sharedState.assistant.chat.history.push({
          sender: "assistant",
          text: response.data
        })
      }).catch(function(error) {
        // TODO: implement actual error handling
        alert(error)
      }).finally(function() {
        sharedState.assistant.chat.disabled = false;
      })

      // Get the sources
      axios.post("/api/v1/vectors/science", {
        query_text: this.chatMessage,
        raw_return: true
      }).then(function(response) {
        return Promise.all(response.data.map(
          (item) => axios.get(`/api/v1/science/articles/${item.id}`)
          )
        )
      }).then(function(response) {
        sharedState.assistant.sources.items = response
        sharedState.assistant.sources.visible = true
      }).catch(function(error) {
        // TODO: implement actual error handling
        alert(error);
      })

      this.chatMessage = ""
    }
  }
}
</script>
