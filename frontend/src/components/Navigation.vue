  <template>
    <header class="bg-white shadow-md border-gray-200">
      <div class="container mx-auto flex items-center justify-between py-3 px-4">
        <button class="text-2xl">
          &#9776;
        </button>
        <div class="text-xl font-bold flex items-center space-x-2">
          <img src="../assets/gerb.png" alt="Logo" class="h-11">
        </div>
        <a href="#" class="font-bold hover:text-gray-600">Личный кабинет</a>
      </div>
      <div class="border-t border-b py-4">
        <div class="flex justify-center items-center">
          <nav class="hidden md:flex justify-evenly w-full text-lg">
            <RouterLink to="analytics" activeClass="font-bold" class="hover:text-gray-600">Аналитика</RouterLink>
            <RouterLink to="news" class="hover:text-gray-600">Новости</RouterLink>
            <RouterLink to="index" class="hover:text-gray-600">Главная</RouterLink>
            <RouterLink to="research" class="hover:text-gray-600">Исследования</RouterLink>
            <RouterLink to="assistant" class="hover:text-gray-600">Ассистент</RouterLink>
          </nav>
        </div>
      </div>
      <div class="container mx-auto flex justify-between py-2 px-4 text-lg text-gray-700">
        <span>Доллар 83,25 ₽/$ <span class="text-red-500">-0,3%</span></span>
        <span>Евро 94,57 ₽/€ <span class="text-green-500">+1,15%</span></span>
        <span>Brent 64,76 $/бар. <span class="text-green-500">+2,26%</span></span>
        <span>S&P 500 5363,36 <span class="text-green-500">+1,81%</span></span>
      </div>
    </header>
  </template>

  <script>
  export default {
    name: "HeaderComponent",
  };
  </script>
