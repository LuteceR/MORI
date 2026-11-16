<script setup lang="ts">
defineProps<{
  project: {
    id_projects: number
    name: string
    description: string
  }
}>()

defineEmits<{
  delete: [projectName: string]
}>()
</script>

<template>
  <UCard
    :title="project.name"
    :description="project.description"
    variant="subtle"
    class="w-full"
  >
    <template #default>
      <UFieldGroup
        orientation="horizontal"
        class="h-10 w-full"
      >
        <UButton
          color="info"
          variant="outline"
          icon="i-lucide-pencil"
          label="Редактировать"
          class="w-full"
          :to="`/project/project/${project.id_projects}`"
        />
        <UButton
          color="error"
          variant="outline"
          icon="i-lucide-trash"
          label="Удалить"
          class="w-full"
          @click="$emit('delete', project.name)"
        />
      </UFieldGroup>
    </template>
  </UCard>
</template>
