<script setup lang="ts">
const props = defineProps<{
  models: string[]
  datasets: string[]
}>()

const modelName = defineModel<string>('modelName', { required: true })
const datasetName = defineModel<string>('datasetName', { required: true })
const filePath = defineModel<string>('filePath', { required: true })
const wordsKey = defineModel<string>('wordsKey', { required: true })
const nerKey = defineModel<string>('nerKey', { required: true })
const showThreshold = defineModel<boolean>('showThreshold', { required: true })
const thresholdValue = defineModel<number>('thresholdValue', { required: true })

const emit = defineEmits<{
  run: []
}>()
</script>

<template>
  <UModal
    title="Запустить модель"
    :dismissible="false"
  >
    <UButton
      label="Запустить модель"
      icon="i-lucide-chart-line"
      color="neutral"
      variant="outline"
    />
    <template #body>
      <USelectMenu
        v-model="modelName"
        class="mb-4 w-[85%]"
        :items="props.models"
        placeholder="Выберете модель"
      />
      <USelectMenu
        v-model="datasetName"
        class="mb-4 w-[85%]"
        :items="props.datasets"
        placeholder="Выберете датасет"
      />
      <UFormField label="Путь до файла">
        <UInput
          v-model="filePath"
          class="mb-4 w-[85%]"
          placeholder="test.jsonl"
          required
        />
      </UFormField>
      <UFormField label="Ключ в файле, где хранится текст">
        <UInput
          v-model="wordsKey"
          class="mb-4 w-[85%]"
          placeholder="words"
          required
        />
      </UFormField>
      <UFormField label="Ключ в файле, где хранится NER-метки">
        <UInput
          v-model="nerKey"
          class="mb-4 w-[85%]"
          placeholder="ner"
          required
        />
      </UFormField>
      <UFormField>
        <div class="flex items-center gap-2">
          <UTooltip text="Если уверенность модели меньше порога, ставится метка 'O'">
            <UCheckbox
              v-model="showThreshold"
              label="Порог"
              size="md"
            />
            <UInput
              v-if="showThreshold"
              v-model="thresholdValue"
              class="w-24"
              type="number"
              step="0.05"
              min="0"
              max="1"
              placeholder="0.5"
            />
          </UTooltip>
        </div>
      </UFormField>
    </template>
    <template #footer="{ close }">
      <UButton
        label="Отмена"
        color="neutral"
        variant="outline"
        @click="close"
      />
      <UButton
        label="Запустить модель"
        color="neutral"
        @click="emit('run'); close()"
      />
    </template>
  </UModal>
</template>
