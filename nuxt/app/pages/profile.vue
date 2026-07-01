<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

import * as z from 'zod';
import type { FormSubmitEvent } from '@nuxt/ui';

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

const schema = z.object({
  projectName: z.string()
    .min(5, "Минимальная длина 5 символов")
    .max(50, "Максимальная длина 50 символов")
    .regex(
      /^[a-zA-Z0-9а-яА-ЯёЁ]+$/,
      "Можно использовать только буквы и цифры"
    ),
  projectDescription: z.string(),
})

type Schema = z.output<typeof schema>

const state = reactive<Schema>({
  projectName: "",
  projectDescription: "",
})

async function createProject(event: FormSubmitEvent<Schema>) {
  try {
    const response = await fetch(new URL('/project', apiBaseProjects), {
      method: "POST",
      headers: {
          "Content-Type": "application/json",
      },
      body: JSON.stringify({
        'project_name' : state.projectName,
        'description' : state.projectDescription,
      }), 
      credentials: "include"
    });

    if (response.status == 200) {
      toast.add({
        title: `Проект ${state.projectName} успешно создан!`,
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
  <UModal 
    :overlay="false" 
    :transition="true" 
    v-model:open='isOpen'
    title="Подтвердите удаление"
    :ui="{
      body: 'flex flex-col w-full space-y-4 items-center',
    }">
    
    <template #body>
      <p>Удалить проект {{ selectedProject }} ?</p>
      <UFieldGroup orientation="horizontal" class="h-10 w-full justify-center">
        <UButton 
          @click="deleteProject(); isOpen = false"
          color="error" 
          variant="outline" 
          icon="i-lucide-trash" 
          label="Подтверждаю" 
          class="w-[40%] justify-center"
        />
      </UFieldGroup>
    </template>
  </UModal>

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

        <UCard 
            v-for="project in projects" 
            :title="project.name"
            :description="project.description"
            variant="subtle"
            class="w-full"
        >
        <template #default>
            <UFieldGroup orientation="horizontal" class="h-10 w-full">
                <UButton color="info" variant="outline" icon="i-lucide-pencil" label="Редактировать" class="w-full" :to="`/project/project/${project.id_projects}`"/>
                <UButton @click='isOpen = true;selectedProject = project.name' color="error" variant="outline" icon="i-lucide-trash" label="Удалить" class="w-full" />
            </UFieldGroup>
        </template>
        </UCard>
    </UPageList>

    <div class="order-first md:order-last flex flex-col p-4">
      <UModal
        :transition="true"
        :ui="{
          body: 'flex flex-col justify-center',
        }">
        <UButton label="Создать проект" icon="i-lucide-plus" variant="outline" class="h-fit w-fit"/>

        <template #header>
          <p>
            Создание проекта
          </p>
        </template>
        
        <template #body>
          <UForm :schema="schema" :state="state" @submit="createProject" class="flex flex-col self-center space-y-4 mt-2 mb-8">
            <UFormField label="Название проекта" name="projectName" >
              <UInput v-model="state.projectName" class="flex justify-center"/>
            </UFormField>

            <UFormField label="Описание" name="projectDescription"  >
              <UInput v-model="state.projectDescription" class="flex justify-center" />
            </UFormField>
            
            <UFieldGroup orientation="horizontal" class="h-10 w-full justify-center">
              <UButton type="submit" color="info" variant="outline" label="Создать" class="w-[40%] justify-center" />
            </UFieldGroup>
          </UForm>
        </template>

      </UModal>
    </div>

  </div>
</template>