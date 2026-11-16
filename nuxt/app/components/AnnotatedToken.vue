<script setup lang="ts">
defineProps<{
  word: string
  rowIndex: number
  wordIndex: number
  colorClass: string
}>()

defineEmits<{
  contextmenu: [event: MouseEvent, rowIndex: number, wordIndex: number]
}>()
</script>

<template>
  <span
    :data-i="rowIndex"
    :data-k="wordIndex"
    :class="colorClass + ' rounded-sm mt-1 pl-1 pr-1'"
    @contextmenu.capture="$emit('contextmenu', $event, rowIndex, wordIndex)"
  >{{ word }}</span>
</template>
