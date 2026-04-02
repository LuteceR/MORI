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
const description = 'МОРИ - Машинное Обучение : Разворачивание и Исследование.'

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
  <UApp :locale="ru">
    <UHeader>
      <template #left>
        <NuxtLink to="/">
          <AppLogo />
        </NuxtLink>
      </template>
      <template #right>
        <UColorModeSelect />
      </template>
    </UHeader>

    <NuxtLayout>
      <NuxtPage />
    </NuxtLayout>

  </UApp>
</template>
