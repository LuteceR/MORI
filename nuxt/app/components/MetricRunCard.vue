<script setup lang="ts">
defineProps<{
  metric: {
    id_metrics: number
    name: string
    name_1: string
    date: string
    metrics_data: Array<{ name: string, value: number }>
  }
  index: number
  editMode: boolean
}>()

defineEmits<{
  remove: []
}>()
</script>

<template>
  <UCard class="m-4 w-[95%]">
    <template #header>
      <div class="text-xl flex justify-between items-center">
        <span>Запуск #{{ index + 1 }}</span>
        <span class="flex items-center">
          <span class="text-sm">{{ metric.date }}</span>
          <UButton
            v-if="editMode"
            icon="i-lucide-x"
            variant="outline"
            size="xs"
            class="ml-3"
            color="error"
            @click="$emit('remove')"
          />
        </span>
      </div>
    </template>
    <div class="flex flex-col md:flex-row md:justify-between md:items-end">
      <div class="max-w-110 md:order-first">
        <div class="w-full">
          Модель {{ metric.name }}
        </div>
        <div class="w-full">
          Датасет {{ metric.name_1 }}
        </div>
        Метрики
        <div class="w-full ml-4">
          <div
            v-for="result in metric.metrics_data"
            :key="result.name"
          >
            <div class="w-full">
              {{ result.name }}: {{ result.value % 1 === 0 ? result.value : result.value.toFixed(4) }}
            </div>
          </div>
        </div>
      </div>
      <UButton
        size="lg"
        label="Подробный отчёт"
        color="primary"
        class="mt-4 md:mt-0 md:order-last"
        leading-icon="i-lucide-arrow-up-right"
        :to="`/metrics/${metric.id_metrics}`"
      />
    </div>
  </UCard>
</template>
