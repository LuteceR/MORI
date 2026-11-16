<script setup lang="ts">
defineProps<{
  datasetPath: string
  showLabelControls: boolean
}>()

defineEmits<{
  toggleFiles: []
  toggleLabels: []
  save: [event: MouseEvent]
}>()
</script>

<template>
  <UContainer class="flex w-full p-5 h-auto items-center max-w-none transform transition-all duration-200">
    <UButton
      icon="i-lucide-panel-right"
      color="neutral"
      variant="ghost"
      aria-label="Toggle sidebar"
      class="mb-auto flex"
      @click="$emit('toggleFiles')"
    />
    <ULink class="ml-4 flex justify-center self-center">{{ datasetPath }}</ULink>
    <UButton
      v-if="showLabelControls"
      icon="i-lucide-palette"
      color="neutral"
      variant="ghost"
      aria-label="Toggle sidebar"
      class="ml-6 mb-auto"
      @click="$emit('toggleLabels')"
    />
    <UButton
      label="Сохранить"
      color="success"
      variant="subtle"
      :ui="{ base: 'ml-auto' }"
      @click="$emit('save', $event)"
    />
    <span class="ml-2 text-success/60">ctrl+s</span>
  </UContainer>
</template>
