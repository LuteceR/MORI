<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const metricsId: number = Number(useRoute().params.id)

const apiBaseProjects = useRuntimeConfig().public.apiBaseProjects as string

interface ErrorLine {
    word_id: number;
    words: string[];
    true_labels: string[];
    pred_labels: string[];
}

interface PerLabelAccuracy {
    [key: string]: number;
}

interface MetricsResponse {
    name: string;
    name_1: string;
    date: string;
    error_lines: ErrorLine[];
    per_label_accuracy: PerLabelAccuracy;
}

var details = await $fetch<MetricsResponse>(`/metrics/details/?metric_id=${metricsId}`, {
    baseURL: apiBaseProjects,
    method: "GET",
    headers: {
        "Content-Type": "application/json",
    },
    credentials: "include"
})

const [datePart, timePart] = details.date.split('T');
details.date = `${timePart?.split('.')[0]} ${datePart}`;

</script>
<template>
    <div class="flex justify-center h-full m-8">
        <div>
            <span>Модель</span>
            <div class="w-full p-5 gap-1 rounded-lg ring-default shadow-lg">  {{ details.name }} </div>
            <span>Датасет</span>
            <div class="w-full p-5 gap-1 rounded-lg ring-default shadow-lg"> Датасет {{ details.name_1 }} </div>
            <span>Дата запуска</span>
            <div class="w-full p-5 gap-1 rounded-lg ring-default shadow-lg"> Дата запуска {{ details.date }} </div>
            <span>Метрики</span>
            <div class="w-full ml-4 p-5 gap-1 rounded-lg ring-default shadow-lg">
                <div v-for="label in Object.keys(details.per_label_accuracy)">
                    <div class="w-full">{{label}}: {{ details.per_label_accuracy[label]?.toFixed(4)  }}</div>
                </div>
            </div>
        </div>
        
        <div class="p-4 max-w-[60%]">
            Ошибки модели  
            <MetricErrorLine
                v-for="(error_line, index) in details.error_lines"
                :key="index"
                :error-line="error_line"
            />
        </div>
    </div> 
</template>