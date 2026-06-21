<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

import type { NavigationMenuItem  } from '@nuxt/ui'

const toast = useToast()
const auth = useAuthStore();
const isSidebarOpened = ref(true)
const colorMode = useColorMode()
const projectId: number = Number(useRoute().params.id)

interface Project {
  id_projects: number
  username: string
  name: string
  description: string
}

interface Model {
  id_models: number
  name: string
  folder_path: string
  id_original_model: string
}

interface Dataset {
  id_datasets: number
  name: string
  url_source: string
  folder_path: string
}

// Это жесть
interface Metric {
  id_metrics: number,
  name: string, // Model
  name_1: string, // Dataset
  date: string,
  metrics_data: Array<MetricResult>,
}

interface MetricResult {
  name: string,
  value: number
}

interface ProjectResponse {
    "project": Project,
    "models": Model[],
    "datasets": Dataset[]
  }

const { data, error, pending } = await useFetch<ProjectResponse>('http://localhost:8004/project',
  {
    query: { project_id: projectId },
    headers: { "Content-Type": "application/json" },
    credentials: "include"
  }
)

const thisProject = computed(() => data.value?.project ||  {
  id_projects: -1,
  username: "",
  name: "Проект не найден",
  description: ""
})

// Возможно, тут перебор со сложностью получения thisModels и thisDatasets
const state = reactive({
  models: [] as Model[],
  datasets: [] as Dataset[]
})

watch(data, (newData) => {
  if (newData?.models) {
    state.models = newData.models
  }
  if (newData?.datasets) {
    state.datasets = newData.datasets
  }
}, { immediate: true })


const metrics = await $fetch<Metric[]>(`http://localhost:8004/metrics?project_id=${projectId}`, {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
    },
    credentials: "include"
  })



// thisModels, thisDatasets содержат все модели/датасеты в проекте
const thisModels = computed(() => state.models)
const thisDatasets = computed(() => state.datasets)
const thisMetrics = ref(metrics)
// Преобразование формата даты-времени находу
thisMetrics.value.forEach((item, index) => {
  if(thisMetrics.value[index]) {
    const [datePart, timePart] = item.date.split('T')
    thisMetrics.value[index].date = `${timePart?.split('.')[0]} ${datePart}`;
  }
});

const avaliableModels = ref<Model[]>([])
const modelToAdd = ref('')
const avaliableDatasets = ref<Dataset[]>([])
const datasetToAdd = ref('')

function showError(error: string, description?: string) {
  toast.add({
    title: error,
    description: description,
    color: 'error',
    icon: 'i-lucide-circle-x',
    duration: 2000
  })
}

function showSuccess(message: string, description?: string) {
  toast.add({
    title: message,
    description: description,
    color: 'success',
    icon: 'i-lucide-circle-check',
    duration: 2000
  })
}

async function getAvaliableModels() {
  try {
    const response = await $fetch<Model[]>("http://localhost:8003/models", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        })
    avaliableModels.value = response
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при получении списка моделей!')
  }
}


async function getAvaliableDatasets() {
  try {
    const response = await $fetch<Dataset[]>("http://localhost:8002/datasets", {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include"
        })   
    avaliableDatasets.value = response
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при получении списка датасетов!')
  }
}


async function addModelToProject() {
  if (!modelToAdd.value) {
    showError('Произошла ошибка при добавлении модели!')
    return
  }
  try {
    await $fetch(`http://localhost:8004/project/model?project_name=${thisProject.value.name}&model_name=${modelToAdd.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
    })
    let model = avaliableModels.value.find(model => model.name === modelToAdd.value)
    if (model) { 
      state.models.push(model)
      showSuccess('Модель успешно добавлена')
    }
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при добавлении модели!')
  }
}


async function addDatasetToProject() {
  if (!datasetToAdd.value) return
  try {
    await $fetch(`http://localhost:8004/project/dataset?project_name=${thisProject.value.name}&dataset_name=${datasetToAdd.value}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
    })
    let dataset = avaliableDatasets.value.find(dataset => dataset.name === datasetToAdd.value)
    if (dataset) {
      state.datasets.push(dataset)
      showSuccess('Датасет успешно добавлен!')
    }
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при добавлении датасета!')
  }
}


async function removeModelFromProject(model: Model) {
  try {
    await $fetch(`http://localhost:8004/project/model?project_name=${thisProject.value.name}&model_name=${model.name}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
    })
    const index = state.models.indexOf(model);
    if (index > -1) {
      state.models.splice(index, 1);
      modelToAdd.value = ''
      showSuccess('Модель успешно удалена из проекта')
    }
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при удалении модели!')
  }
}


async function removeDatasetFromProject(dataset: Dataset) {
  try {
    await $fetch(`http://localhost:8004/project/dataset?project_name=${thisProject.value.name}&dataset_name=${dataset.name}`, {
      method: 'DELETE',
      headers: { 'Content-Type': 'application/json' },
      credentials: "include",
    })
    const index = state.datasets.indexOf(dataset);
    if (index > -1) {
      state.datasets.splice(index, 1);
      datasetToAdd.value = ''
      showSuccess('Датасет успешно удален из проекта')
    }
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при удалении датасета!')
  }
}

const isModelRunning = ref(false)
const runFilePath = ref('test.jsonl')
const runWordsKey = ref('words')
const showThreshold = ref(false)
const thresholdValue = ref<number>(0.5)

async function runModel() {
  if (runFilePath.value == '' || runWordsKey.value == '') {
    showSuccess(runFilePath.value == ''? 'Укажите путь до файла': 'Укажите json-ключ')
    return
  }
  try {
    isModelRunning.value = true
    const metrics = await $fetch(
      `http://localhost:8004/project/run?` +
      `project_name=${thisProject.value.name}&` +
      `model_name=${modelToAdd.value}&` +
      `dataset_name=${datasetToAdd.value}&` +
      `filepath=${runFilePath.value}&` +
      `text_key=${runWordsKey.value}` +
      (showThreshold.value ? `&threshold=${thresholdValue.value}` : ''),
      {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include'
      }
    )
    
    showSuccess('Запуск модели завершен!')
  } catch (e) {
    console.error(e)
    showError('Произошла ошибка при запуске модели!')
  } finally {
    isModelRunning.value = false
  }
}
</script>


<template>
  <div class="flex flex-1">
    <USidebar
      v-model:open="isSidebarOpened"
      collapsible="icon"
      :ui="{
          gap: 'h-[calc(100%-var(--ui-header-height))]',
          container:
            'absolute top-(--ui-header-height) bottom-0 h-[calc(100%-var(--ui-header-height))]'
        }"
    >  
      <template #default="{ state }">
        <UModal title="Добавить модель" :dismissible="false">
          <UButton 
            label='Добавить модель' 
            icon='i-lucide-brain' 
            color="neutral" 
            variant="outline"
            @click="getAvaliableModels"
          />
          <template #body>
            <USelectMenu v-model="modelToAdd" :items="avaliableModels.map(model => model.name)" placeholder="Выберете модель"/>
          </template>

          <template #footer="{ close }">
            <UButton label="Отмена" color="neutral" variant="outline" @click="close" />
            <UButton label="Добавить в проект" color="neutral" @click="addModelToProject(); close()"/>
          </template>
        </UModal>

        <UModal title="Добавить датасет" :dismissible="false">
          <UButton 
            label='Добавить датасет' 
            icon='i-lucide-astroid' 
            color="neutral" 
            variant="outline"
            @click="getAvaliableDatasets"
          />
          <template #body>
            <USelectMenu v-model="datasetToAdd" :items="avaliableDatasets.map(dataset => dataset.name)" placeholder="Выберете датасет"/>
          </template>

          <template #footer="{ close }">
            <UButton label="Отмена" color="neutral" variant="outline" @click="close" />
            <UButton label="Добавить в проект" color="neutral" @click="addDatasetToProject(); close()"/>
          </template>
        </UModal>
        
        <UModal title="Запустить модель" :dismissible="false">
          <UButton 
            label='Запустить модель' 
            icon='i-lucide-chart-line' 
            color="neutral"
            variant="outline"
            @click=""
          />
          <template #body>
            <USelectMenu class="mb-4 w-[85%]" v-model="modelToAdd" :items="thisModels.map(model => model.name)" placeholder="Выберете модель"/>
            <USelectMenu class="mb-4 w-[85%]" v-model="datasetToAdd" :items="thisDatasets.map(dataset => dataset.name)" placeholder="Выберете датасет"/>
            <UFormField label="Путь до файла">
              <UInput class="mb-4 w-[85%]" v-model="runFilePath" placeholder="test.jsonl"/>
            </UFormField>
            <UFormField label="Json-ключ в файле, где хранится текст">
              <UInput class="mb-4 w-[85%]" v-model="runWordsKey" placeholder="words"/>
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
                  v-if="showThreshold"v-model="thresholdValue" class="w-24"
                  type="number" step="0.05" min="0" max="1" placeholder="0.5"
                />
                </UTooltip>
              </div>
            </UFormField>
          </template>

          <template #footer="{ close }">
            <UButton label="Отмена" color="neutral" variant="outline" @click="close" />
            <UButton label="Запустить модель" color="neutral" @click="runModel(); close()"/>
          </template>
        </UModal>
      </template>

      <!-- <template #footer>
        <UButton
            icon="i-lucide-panel-left"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            @click="isSidebarOpened = !isSidebarOpened"
        />
      </template> -->
    </USidebar>
    <div class="flex flex-col lg:w-[75%] sm:w-[65%] h-screen gap-6 p-8 transform transition-all duration-200 max-h-screen">
      <div h-(--ui-header-height) shrink-0 flex items-center px-4>
          <UButton
            icon="i-lucide-panel-left"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            @click="isSidebarOpened = !isSidebarOpened"
          />
      
        <span class="text-default text-3xl ml-4">{{ thisProject.name.split('/')[1] || thisProject.name }}</span>
        <UButton class="ml-4"
          icon='i-lucide-pencil' 
          color="neutral" 
          variant="ghost"
          @click="" 
          disabled
        />
        <div v-if="isModelRunning" class="w-full h-20 shrink-0 mt-2">
          <div class="flex items-center">
            <UButton size="lg" variant="ghost" color="neutral" leadingIcon='i-lucide-shell' class="animate-spin"/>
            <span class="ml-4">Модель расчитывает ответы...</span>
          </div>
        </div>
      </div>
      <UScrollArea>
        <div v-if="thisMetrics.length === 0" class="text-center h-dvh">
          Вы ещё не запускали модели в этом проекте
        </div>
        <UCard v-for="(metric, index) in thisMetrics" :key="metric.id_metrics" class="m-4 w-full">
          <template #header>
            <div class="text-xl flex justify-between items-center">
              <span> Запуск #{{ index + 1 }} </span>
              <span class="text-sm"> {{ metric.date }} </span>
            </div>
          </template>
          <div class="flex justify-between items-end">
            <div class="max-w-110">
              <div class="w-full"> Модель {{ metric.name }} </div>
              <div class="w-full"> Датасет {{ metric.name_1 }} </div>
              Метрики  
              <div class="w-full ml-4">
                <div v-for="m_result in metric.metrics_data">
                  <div class="w-full"> {{ m_result.name }}: {{ m_result.value % 1 == 0? m_result.value:  m_result.value.toFixed(4)}} </div>
                </div>
              </div>
            </div>
            <UButton 
                size="lg" 
                label="Подробный отчёт" 
                color="primary" 
                leadingIcon='i-lucide-arrow-up-right'
                :to="`/metrics/${metric.id_metrics}`"
            />  
          </div> 
        </UCard>
      </UScrollArea>
    </div>
    
    <USeparator orientation="vertical" class="h-screen" />
    <div class="flex flex-col lg:w-[25%] sm:w-[35%] gap-3 p-4 max-h-screen overflow-y-auto transform transition-all duration-200">
      <div class="text-default font-medium">
        Модели проекта:
      </div>
      <UScrollArea class="h-[40%] w-full shrink-0 scrollbar-none ring-gray-600 rounded-lg ring shadow-lg">
        <UCard :ui="{ body: 'p-3 sm:p-3' }" v-for="model in thisModels" :key="model.id_models" class="m-4 ">
          <span class="font-medium flex justify-between">
            {{ model.name.split('/')[1] || model.name }}
            <UButton 
              icon="i-lucide-x" 
              variant="ghost" 
              size="xs"
              class="hover:bg-gray-100"
              color="error"
              @click="removeModelFromProject(model)"
            />
          </span>
          <template v-if="model.id_original_model" class="text-gray-400">            
            {{ model.id_original_model }}
          </template>
          <div class="text-sm">
            {{ model.name.split('/')[0] || model.name }}
          </div>
        </UCard>
      </UScrollArea>    
      
      <div class="text-default font-medium mt-3">
        Датасеты проекта:
      </div>
      <UScrollArea class="h-[40%] w-full shrink-0 scrollbar-none ring-gray-600 rounded-lg ring shadow-lg">
        <UCard :ui="{ body: 'p-3 sm:p-3' }" v-for="dataset in thisDatasets" :key="dataset.id_datasets" class="m-4">
          <span class="font-medium flex justify-between">
            <ULink  as="button" :to="'/dataset/' + dataset.name" class="flex self-center">
              {{ dataset.name.split('/')[1] || dataset.name }}
            </ULink>
            <UButton 
                icon="i-lucide-x" 
                variant="ghost" 
                size="xs"
                class="hover:bg-gray-100"
                color="error"
                @click="removeDatasetFromProject(dataset)"
              />
          </span>
          <div class="text-sm">
            {{ dataset.name.split('/')[0] || dataset.name }}
          </div>
        </UCard>    
      </UScrollArea>
    </div>
  </div>
</template>