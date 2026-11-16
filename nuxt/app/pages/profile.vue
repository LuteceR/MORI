<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const apiBaseProjects = useRuntimeConfig().public.apiBaseProjects as string

const toast = useToast()
const auth = useAuthStore();
await auth.fetchUser();

interface Project {
  id_projects: number
  username: string
  name: string
  description: string
}

const projects = ref<Project[]>([])

async function requestProjects() {
  try {
    const response = await $fetch<Project[]>("/projects", {
            baseURL: apiBaseProjects,
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

async function createProject(values: { projectName: string; projectDescription: string }) {
  try {
    const response = await fetch(new URL('/project', apiBaseProjects), {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({
        'project_name' : values.projectName,
        'description' : values.projectDescription,
      }), 
      credentials: "include"
    });

    if (response.status == 200) {
      toast.add({
        title: `Проект ${values.projectName} успешно создан!`,
        color: 'success',
      })

      await requestProjects();
    }
  } catch (e) {
    // дебаг ошибок
    // toast.add({
    //   title: "Произошла ошибка!",
    //   description: e.message,
    //   color: 'error',
    // });
  }
}

async function deleteProject() {
  try {
    const response = await fetch(new URL('/project', apiBaseProjects), {
      method: "DELETE",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({
        'project_name' : selectedProject.value,
      }), 
      credentials: "include"
    });

    await requestProjects();
    if (response.status == 200) {
      toast.add({
        icon: 'i-lucide-check',
        title: `Проект ${selectedProject.value} успешно удалён!`,
        color: 'success',
      })
    } else {
      toast.add({
        icon: 'i-lucide-frown',
        title: 'Произошла ошибка!',
        description: `Проект ${selectedProject.value} не удалён`,
        color: 'error',
      })
    }
  } catch(e) {
    // дебаг ошибок
    // toast.add({
    //   title: "Произошла ошибка!",
    //   description: e.message,
    //   color: 'error',
    // });
  }
}

const isOpen = ref(false);
const selectedProject = ref('');
onMounted(requestProjects)
</script>

<template>
  <ProjectDeleteModal
    v-model:open="isOpen"
    :project-name="selectedProject"
    @confirm="deleteProject"
  />

  <div class="m-auto mt-3 max-w-60">
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
      <path fill="currentColor" d="M12 4a4 4 0 1 1 0 8a4 4 0 0 1 0-8m0 16s8 0 8-2c0-2.4-3.9-5-8-5s-8 2.6-8 5c0 2 8 2 8 2" />
    </svg>
    <div class="mx-auto text-2xl font-semibold text-center">{{ auth.user.login }}</div>
  </div>
    

  <div class="flex flex-col md:flex-row h-full w-full mt-15 m-auto justify-center">
    <UPageList class="order-last md:order-first flex flex-col mb-auto rounded-t h-full min-w-[50%] xl:w-160 p-4 gap-4 ring ring-default shadow-sm">
        
        <div v-if="projects.length === 0" class="text-center h-dvh">
        У вас нет проектов
        </div>

        <ProjectCard
          v-for="project in projects"
          :key="project.id_projects"
          :project="project"
          @delete="selectedProject = $event; isOpen = true"
        />
    </UPageList>

    <div class="order-first md:order-last flex flex-col p-4">
      <ProjectCreateModal @submit="createProject" />
    </div>

  </div>
</template>