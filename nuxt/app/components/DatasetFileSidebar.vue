<script setup lang="ts">
import type { TreeItem } from '@nuxt/ui'

defineProps<{
  items?: TreeItem[]
}>()

const open = defineModel<boolean>('open', { required: true })
</script>

<template>
  <USidebar
    v-model:open="open"
    variant="sidebar"
    collapsible="offcanvas"
    side="left"
    :ui="{
      gap: 'h-[calc(100%-var(--ui-header-height))]',
      container: 'absolute top-(--ui-header-height) bottom-0 h-[calc(100%-var(--ui-header-height))]'
    }"
  >
    <div class="flex h-[5%] w-auto justify-center items-center">
      <h1>Файлы</h1>
    </div>
    <div class="p-2 rounded-lg ring ring-default shadow-lg">
      <UTree
        :items="items"
        orientation="vertical"
        :ui="{
          link: 'p-1.5 overflow-hidden',
          listWithChildren: 'ml-3'
        }"
      />
    </div>
  </USidebar>
</template>
