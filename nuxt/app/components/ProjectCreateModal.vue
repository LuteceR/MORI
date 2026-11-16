<script setup lang="ts">
import { reactive } from 'vue'
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const emit = defineEmits<{
  submit: [values: { projectName: string, projectDescription: string }]
}>()

const schema = z.object({
  projectName: z.string()
    .min(5, 'Минимальная длина 5 символов')
    .max(50, 'Максимальная длина 50 символов')
    .regex(/^[a-zA-Z0-9а-яА-ЯёЁ]+$/, 'Можно использовать только буквы и цифры'),
  projectDescription: z.string()
})

type Schema = z.output<typeof schema>

const state = reactive<Schema>({
  projectName: '',
  projectDescription: ''
})

function submit(event: FormSubmitEvent<Schema>) {
  emit('submit', event.data)
}
</script>

<template>
  <UModal
    :transition="true"
    :ui="{ body: 'flex flex-col justify-center' }"
  >
    <UButton
      label="Создать проект"
      icon="i-lucide-plus"
      variant="outline"
      class="h-fit w-fit"
    />
    <template #header>
      <p>Создание проекта</p>
    </template>
    <template #body>
      <UForm
        :schema="schema"
        :state="state"
        class="flex flex-col self-center space-y-4 mt-2 mb-8"
        @submit="submit"
      >
        <UFormField
          label="Название проекта"
          name="projectName"
        >
          <UInput
            v-model="state.projectName"
            class="flex justify-center"
          />
        </UFormField>
        <UFormField
          label="Описание"
          name="projectDescription"
        >
          <UInput
            v-model="state.projectDescription"
            class="flex justify-center"
          />
        </UFormField>
        <UFieldGroup
          orientation="horizontal"
          class="h-10 w-full justify-center"
        >
          <UButton
            type="submit"
            color="info"
            variant="outline"
            label="Создать"
            class="w-[40%] justify-center"
          />
        </UFieldGroup>
      </UForm>
    </template>
  </UModal>
</template>
