<script setup lang="ts">
defineProps<{
  marks: Map<string, string>
}>()

const open = defineModel<boolean>('open', { required: true })
</script>

<template>
  <USidebar
    v-model:open="open"
    variant="inset"
    title="Цвета тегов"
    collapsible="offcanvas"
    side="right"
    mode="slideover"
    :ui="{
      root: 'h-[20svh]',
      container: 'flex flex-col mt-4 rounded-lg ring ring-default shadow-lg top-(--ui-header-height) bottom-0 h-[calc(80%-var(--ui-header-height))]'
    }"
  >
    <UBadge
      v-for="[label, colorClass] in marks"
      :key="label"
      class="text-gray font-medium"
      :label="label"
      variant="soft"
      :class="colorClass"
    />
  </USidebar>
</template>
