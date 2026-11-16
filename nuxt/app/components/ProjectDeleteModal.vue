<script setup lang="ts">
defineProps<{
  projectName: string
}>()

const open = defineModel<boolean>('open', { required: true })

defineEmits<{
  confirm: []
}>()
</script>

<template>
  <UModal
    v-model:open="open"
    :overlay="false"
    :transition="true"
    title="Подтвердите удаление"
    :ui="{ body: 'flex flex-col w-full space-y-4 items-center' }"
  >
    <template #body>
      <p>Удалить проект {{ projectName }} ?</p>
      <UFieldGroup
        orientation="horizontal"
        class="h-10 w-full justify-center"
      >
        <UButton
          color="error"
          variant="outline"
          icon="i-lucide-trash"
          label="Подтверждаю"
          class="w-[40%] justify-center"
          @click="$emit('confirm'); open = false"
        />
      </UFieldGroup>
    </template>
  </UModal>
</template>
