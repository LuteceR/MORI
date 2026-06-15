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

function convertToFormat(error_line: ErrorLine) {

}

</script>
<template>
    <div class="flex justify-between items-end">
        <div class="max-w-110">
            <div class="w-full"> Модель {{ details.name }} </div>
            <div class="w-full"> Датасет {{ details.name_1 }} </div>
            <div class="w-full"> Дата запуска {{ details.date }} </div>
            Метрики  
            <div class="w-full ml-4">
                <div v-for="label in Object.keys(details.per_label_accuracy)">
                    <div class="w-full">{{label}}: {{ details.per_label_accuracy[label]?.toFixed(4)  }}</div>
                </div>
            </div>
            Ошибки модели  
            <div class="container mx-auto p-4">
                <div 
                v-for="(error_line, index) in details.error_lines" 
                :key="index"
                class="mb-6 p-4 border rounded-lg"
                >
                <div class="w-full">
                    <div class="text-sm mb-2">
                    Word ID: {{ error_line.word_id }}
                    </div>
                    <div class="flex flex-wrap gap-2">
                    <div 
                        v-for="(word, wordIndex) in error_line.words"
                        :key="wordIndex"
                        class="relative inline-block"
                    >
                        <div :class="[
                                'px-2 py-1 rounded relative group',
                                wordIndex === error_line.word_id 
                                ? 'border-2 border-red-500' 
                                : 'border'
                            ]">
                        <span class="text-sm">{{ word }}</span>
                        </div>
                        
                        <!-- Метки над словом (показываем при наведении или всегда) -->
                        <div class="absolute -top-8 left-0 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity duration-200 pointer-events-none">
                            <div class="flex gap-1">
                                <span class="px-1 py-0.5 bg-green-100 text-green-800 rounded">
                                true: {{ error_line.true_labels[wordIndex] }}
                                </span>
                                <span class="px-1 py-0.5 bg-blue-100 text-blue-800 rounded">
                                pred: {{ error_line.pred_labels[wordIndex] }}
                                </span>
                            </div>
                        </div>
                    </div>
                    </div>
                </div>
                </div>
            </div>
        </div> 
    </div> 
</template>