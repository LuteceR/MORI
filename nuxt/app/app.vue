<script setup>
useHead({
  meta: [
    { name: 'viewport', content: 'width=device-width, initial-scale=1' }
  ],
  link: [
    { rel: 'icon',
      type: 'image/svg+xml',
      href: '/logo.svg',
      sizes: '64x64' }
  ],
  htmlAttrs: {
    lang: 'ru'
  }
})

const title = 'МОРИ'
const description = 'МОРИ - Машинное Обучение: Разворачивание и Исследование.'
const route = useRoute()
const search = ref('');
const router = useRouter();

function handleSearch() {
  if (search.value.trim()) {
    router.push({ path: '/search', query: { search: search.value } });
  }
}

useSeoMeta({
  title,
  description,
  ogTitle: title,
  ogDescription: description,
  ogImage: 'https://ui.nuxt.com/assets/templates/nuxt/starter-light.png',
  twitterImage: 'https://ui.nuxt.com/assets/templates/nuxt/starter-light.png',
  twitterCard: 'summary_large_image'
})
</script>

<template>
  <UApp>
    <UHeader :toggle="false">
      <template #left>
        <NuxtLink to="/">
          <AppLogo />
        </NuxtLink>
        <UInput 
          v-model="search" 
          v-if="!['/search', '/auth', '/reg'].includes(route.path)" 
          color='info' 
          class='lg:ml-4 sm:ml-4 transform transition-all duration-400 sm:w-60 md:w-70 lg:w-90' 
          icon="i-lucide-search" 
          size="md" 
          variant="outline" 
          placeholder="Поиск..."
          @keyup.enter="handleSearch"
        />
      </template>
      <template #right>
        <UColorModeSelect />
        <ProfileIcon />
      </template>
    </UHeader>
    
    <UMain class="flow-root">
      <NuxtLayout>
        <NuxtPage />
      </NuxtLayout>
    </UMain>

  </UApp>
</template>
