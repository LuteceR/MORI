<script setup lang="ts">
defineProps<{
  errorLine: {
    word_id: number
    words: string[]
    true_labels: string[]
    pred_labels: string[]
  }
}>()

function truncate(value: string, max: number) {
  return value.length > max ? `${value.slice(0, max)}...` : value
}
</script>

<template>
  <div class="mb-6 p-4 border rounded-lg mr-auto">
    <div class="flex flex-wrap gap-2">
      <div
        v-for="(word, wordIndex) in errorLine.words"
        :key="wordIndex"
        class="inline-block"
      >
        <UPopover>
          <div
            :class="[
              'px-2 py-1 rounded',
              wordIndex === errorLine.word_id ? 'border-2 border-red-500' : 'border'
            ]"
          >
            <span class="text-sm">{{ truncate(word, 50) }}</span>
          </div>
          <template #content>
            <div class="flex gap-1">
              <span class="px-1 py-0.5 bg-green-100 text-green-800 rounded">
                pred: {{ errorLine.pred_labels[wordIndex] }}
              </span>
              <span class="px-1 py-0.5 bg-blue-100 text-blue-800 rounded">
                true: {{ errorLine.true_labels[wordIndex] }}
              </span>
            </div>
          </template>
        </UPopover>
      </div>
    </div>
  </div>
</template>
