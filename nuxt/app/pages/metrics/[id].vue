<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

const metricsId: number = Number(useRoute().params.id)


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

var details = await $fetch<MetricsResponse>(`http://localhost:8004/metrics/details/?metric_id=${metricsId}`, {
    method: "GET",
    headers: {
        "Content-Type": "application/json",
    },
    credentials: "include"
})

const [datePart, timePart] = details.date.split('T');
details.date = `${timePart?.split('.')[0]} ${datePart}`;

function truncate(str: string, max: number) {
  return str.length > max ? str.slice(0, max) + "..." : str;
}

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
            <div v-for="(error_line, index) in details.error_lines" 
                :key="index"
                class="mb-6 p-4 border rounded-lg mr-auto"
            >
                <div class="flex flex-wrap gap-2">
                    <div 
                        v-for="(word, wordIndex) in error_line.words"
                        :key="wordIndex"
                        class="inline-block"
                    >
                        <UPopover>
                            <div :class="[
                                    'px-2 py-1 rounded',
                                    wordIndex === error_line.word_id 
                                    ? 'border-2 border-red-500' 
                                    : 'border'
                                ]">
                                <span class="text-sm">{{ truncate(word, 50) }}</span>
                            </div>
                            
                            <template #content>
                                <div class="flex gap-1">
                                    <span class="px-1 py-0.5 bg-green-100 text-green-800 rounded">
                                    pred: {{ error_line.true_labels[wordIndex] }}
                                    </span>
                                    <span class="px-1 py-0.5 bg-blue-100 text-blue-800 rounded">
                                    true: {{ error_line.pred_labels[wordIndex] }}
                                    </span>
                                </div>
                            </template>
                        </UPopover>
                    </div>
                </div>
            </div>
        </div>
    </div> 
</template>