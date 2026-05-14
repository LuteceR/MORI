<script setup lang="ts">
interface Project {
  username: string
  name: string
  description: string
}

const projects = ref<Project[]>([])

async function requestProjects() {
  try {
    const response = await $fetch<Project[]>("http://localhost:8000/projects", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        })
    
    if (response.length === 0) {
      projects.value = []
      return
    }
    
    projects.value = response
  } catch (e) {
    console.error(e)
    projects.value = []
  }
}

onMounted(requestProjects)
</script>

<template>
    <div class="m-auto mt-3 max-w-60 text-gray-300">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12 4a4 4 0 1 1 0 8a4 4 0 0 1 0-8m0 16s8 0 8-2c0-2.4-3.9-5-8-5s-8 2.6-8 5c0 2 8 2 8 2" />
        </svg>
        <div class="mx-auto text-center">Вы</div>
    </div>
    <div class="mx-auto max-w-3xl mt-3 text-gray-300">
        Ваши проекты:
    </div>
    <UPageList class="mt-4 max-w-3xl mx-auto gap-10"> 
        <div v-if="projects.length === 0" class="text-center py-12 text-gray-300">
        У вас нет проектов
        </div>
        <UCard 
            v-for="project in projects" 
            :key="project.name"
            class="w-full hover:shadow-lg transition-shadow bg-gray-800"
        >
            <template #header>
            <div class="flex justify-between">
                <span class="font-semibold text-lg mb-1">{{ project.name }}</span>
                <span class="text-sm text-gray-500">Владелец: {{ project.username }}</span>
            </div>
            <p class="mt-2 text-gray-300">Описание: {{ project.description || 'Описание отсутствует' }}</p>
            </template>
        </UCard>
    </UPageList>
</template>