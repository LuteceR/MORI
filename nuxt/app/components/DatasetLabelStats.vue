<script setup lang="ts">
import Chart from 'primevue/chart'

defineProps<{
  data: {
    labels: string[]
    datasets: Array<{
      data: number[]
      backgroundColor: string[]
      minBarLength: number
    }>
  }
  options: {
    plugins: {
      legend: {
        labels: {
          usePointStyle: boolean
        }
      }
    }
  }
}>()
</script>

<template>
  <div
    id="chartsidebar"
    class="absolute z-100 p-4 -left-185 mb-auto bottom-0 bg-slate-900 h-150 w-180 rounded-lg ring ring-default shadow-lg"
  >
    <p class="flex justify-center mt-2 mb-2 w-full">
      Характеристики
    </p>
    <ClientOnly>
      <Chart
        class="h-full"
        type="bar"
        :data="data"
        :options="options"
      />
    </ClientOnly>
  </div>
</template>
