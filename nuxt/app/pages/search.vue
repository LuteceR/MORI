<script setup lang="ts">
definePageMeta({
    middleware: "auth",
})

import { gsap } from 'gsap';
import { SiTensorflow, SiPytorch, SiAkamai } from 'vue-icons-plus/si';
import { GrLicense } from "vue-icons-plus/gr";
import { VList } from "virtua/vue";
import type { DropdownMenuItem } from "@nuxt/ui";
import { toast } from 'vue-sonner';
import ISO6391 from 'iso-639-1';
import { meta } from 'zod/v4/core';
import { ItemResizeObserver } from 'virtua/unstable_core';
import { fi } from 'zod/v4/locales';
import { string } from 'zod';

interface ModelCardData {
    type: 'models',
    id: number,
    name: string,
    language?: string[] | string,
    license?: string,
    license_name?: string,
    license_link?: string,
    tags?: string[] | string,
    library_name?:string,
    widget?: string[],
    thumbnail?: string,
    datasets?: string[] | string,
    pipeline_tag?: string,
    base_model?: string[] | string,
    buckets?: string[] | string,
    new_version?: string,
}

interface DatasetCardData {
    type: 'datasets',
    id: number,
    name: string,
    pretty_name: string,
    language?: string[] | string,
    size_categories?: string[],
    source_datasets?: string[] | string,
    license?: string[] | string,
    tags?: string[] | string,
    task_categories?: string[] | string,
    task_ids?: string[] | string,
}

const Toast = useToast();
const searchType = ref<'models' | 'datasets' | 'all'>('all')
const allResults = ref<(ModelCardData | DatasetCardData)[]>([])
const route = useRoute();

const highlightMatch = (text: string, search: string) => {
    if (!search || !text) return [{ text, highlight: false }]

    const ind = text.toLowerCase().indexOf(search.toLowerCase());
    if (ind === -1) return [{ text, highlight: false }]

    const before = text.slice(0, ind);
    const match = text.slice(ind, ind + search.length);
    const after = text.slice(ind + search.length);

    return [
        { text: before, highlight: false },
        { text: match, highlight: true },
        { text: after, highlight: false }
    ]
}

const uniqueFilters = ref({
    method: new Set(),
    library_name: new Set(),
    tags: new Set(),
    language: new Set(),
});

const filter = ref({
    searchFilter: '',
    method: new Set(),
    library_name: new Set(),
    tags: new Set(),
    language: new Set(),
});

const currentData = computed(() => {
    // console.log("filter: ", filter.value);

    return allResults.value.filter(item => 
        {
            if (item.type == "datasets") {

                // ---- фильтр по названию ----
                if (filter.value.searchFilter != '') {
                    if (item.name.includes(filter.value.searchFilter)) {
                        return true
                    }
                    return false
                }

                // ---- фильтр на языки ----
                if (filter.value.language.size > 0) {
                    let itemLanguages: string[] = [];

                    if (Array.isArray(item.language)) {
                        itemLanguages = item.language!
                    } else if (item.language) {
                        itemLanguages = [item.language]
                    }
    
                    const hasCommonLang = itemLanguages.some(lang => {
                        // console.log("lang: ", lang)
                        // console.log("filter: ", filter.value.language)
                        return filter.value.language.has(lang);
                    });
                    
                    if (!hasCommonLang) return false;
                }

                // ---- фильтр на теги ----
                if (filter.value.tags.size > 0) {
                    let itemTags: string[] = [];

                    if (Array.isArray(item.tags)) {
                        itemTags = item.tags;
                    } else {
                        itemTags = [item.tags!];
                    }
    
                    const hasCommonTags = itemTags.some(tag => {
                        // console.log('lib: ', tag)
                        // console.log('filter:', filter.value.tags);
                        return filter.value.tags.has(tag);
                    })
    
                    if (!hasCommonTags) return false;
                }
            } 
            if (item.type == "models") {

                // ---- фильтр по названию ----
                if (filter.value.searchFilter != '') {
                    if (item.name.includes(filter.value.searchFilter)) {
                        return true
                    }
                    return false
                }

                // ---- фильтр на языки ----
                if (filter.value.language.size > 0) {
                    let itemLanguages: string[] = [];
                    
                    if (Array.isArray(item.language)) {
                        itemLanguages = item.language!
                    } else if (item.language) {
                        itemLanguages = [item.language]
                    }
    
                    const hasCommonLang = itemLanguages.some(lang => {
                        // console.log("lang: ", lang)
                        // console.log("filter: ", filter.value.language)
                        return filter.value.language.has(lang);
                    });
                    
                    if (!hasCommonLang) return false;
                }

                // ---- фильтр на библиотеки ----
                if (filter.value.library_name.size > 0) {
                    let itemLibraries: string[] = [];

                    if (Array.isArray(item.library_name)) {
                        itemLibraries = item.library_name;
                    } else {
                        itemLibraries = [item.library_name!];
                    }
    
                    const hasCommonLibrary = itemLibraries.some(lib => {
                        // console.log('lib: ', lib)
                        // console.log('filter:', filter.value.library_name);
                        return filter.value.library_name.has(lib);
                    })
    
                    if (!hasCommonLibrary) return false;
                }

                // ---- фильтр на теги ----
                if (filter.value.tags.size > 0) {
                    let itemTags: string[] = [];

                    if (Array.isArray(item.tags)) {
                        itemTags = item.tags;
                    } else {
                        itemTags = [item.tags!];
                    }
    
                    const hasCommonTags = itemTags.some(tag => {
                        // console.log('lib: ', tag)
                        // console.log('filter:', filter.value.tags);
                        return filter.value.tags.has(tag);
                    })
    
                    if (!hasCommonTags) return false;
                }

            }
            return true;
        }
    )
})

const modes = ref<DropdownMenuItem[][]>([
    [
        {
            label: 'Всё',
            type: 'link',
            onSelect: (e: Event) => {
                searchType.value = "all";
                // console.log(e);
            }
        }
    ],
    [
        {
            label: 'Датасеты',
            type: 'link',
            onSelect: (e: Event) => {
                searchType.value = "datasets";
                // console.log(e);
            }
        }
    ],
    [
        {
            label: 'Модели',
            type: 'link',
            onSelect: (e: Event) => {
                searchType.value = "models";
                // console.log(e);
            }
        }
    ]
])

const languageItems = (lang: string[] | string): DropdownMenuItem[][] => {
    if (!lang) return [];

    const languages = Array.isArray(lang) ? lang : [lang];
    const result: DropdownMenuItem[] = languages.map(l => ({ label: ISO6391.getName(l) }));
    
    return [result]
}

async function fetchModelsCards() {
    const response = await fetch(
        "http://localhost:8003/get_models_metadata",
    {
        credentials: "include"
    })
    
    if (!response.body) return;

    if (response.status != 200) {
        Toast.add({
                color: "error",
                title: "Произошла ошибка при загрузке моделей",
                icon: 'i-lucide-wifi-off',
                ui: {
                    description: 'whitespace-pre-line'
                }
            })  
        return;
    }

    const reader = response.body
                        .pipeThrough(new TextDecoderStream())
                        .getReader();
    
    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        let id = 0;
        const lines = value.split("\n");
        for (const line of lines) {
            if (line.trim()) {
                const metadata = await JSON.parse(line) as ModelCardData;
                
                if (metadata.library_name != undefined || metadata.library_name != null) {
                    uniqueFilters.value.library_name.add(metadata.library_name);
                }

                if (Array.isArray(metadata.tags)) {
                    metadata.tags.forEach(item => uniqueFilters.value.tags.add(item))
                } else if (metadata.tags != undefined || metadata.tags != null) {
                    uniqueFilters.value.tags.add(metadata.tags);
                }

                if (Array.isArray(metadata.language)) {
                    metadata.language.forEach(item => uniqueFilters.value.language.add(item))
                } else if (metadata.language != undefined || metadata.language != null) {
                    uniqueFilters.value.language.add(metadata.language);
                }

                metadata['id'] = id;
                metadata['type'] = "models";
                id++;
                allResults.value.push(metadata)
                // console.log("MODEL\n", metadata)
            }
        }
    }
}

async function fetchDatasetsCards() {
    const response = await fetch(
        "http://localhost:8002/datasets",
        {
            credentials: "include"
        })

    if (!response.body) return;
    
    if (response.status != 200) {
        Toast.add({
                color: "error",
                title: "Произошла ошибка при загрузке датасетов",
                icon: 'i-lucide-wifi-off',
                ui: {
                    description: 'whitespace-pre-line'
                }
            })  
        return;
    }

    const reader = response.body
                    .pipeThrough(new TextDecoderStream())
                    .getReader();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        let id = 0;
        const lines = value.split("\n");
        for (const line of lines) {
            if (line.trim()) {
                const metadata = await JSON.parse(line) as DatasetCardData;
                metadata['id'] = id;
                metadata['type'] = "datasets";

                if (Array.isArray(metadata.language)) {
                    metadata.language.forEach(item => uniqueFilters.value.language.add(item))
                } else if (metadata.language != undefined || metadata.language != null) {
                    uniqueFilters.value.language.add(metadata.language);
                }

                id++;
                allResults.value.push(metadata)
                // console.log("DATASET\n", metadata)
            }
        }
    }
}

function toggleLangButton(event) {
    const langName = ISO6391.getCode(event.target.textContent).toLowerCase().trim();

    if (filter.value.language.has(langName)) {
        filter.value.language.delete(langName);
    } else {
        filter.value.language.add(langName);
    }
}

function toggleMethodButton(event) {
    const tags = event.target.textContent.toLowerCase().trim();
    
    if (filter.value.tags.has(tags)) {
        filter.value.tags.delete(tags);
    } else {
        filter.value.tags.add(tags);
    }
}

function toggleLibraryButton(event) {
    const library_name = event.target.textContent.toLowerCase().trim();
    
    if (filter.value.library_name.has(library_name)) {
        filter.value.library_name.delete(library_name);
    } else {
        filter.value.library_name.add(library_name);
    }
}

onMounted(() => {
    fetchModelsCards();
    fetchDatasetsCards();
    
    if (route.query.search != undefined || route.query.search != null) {
        filter.value.searchFilter = route.query.search as string;
    }

    console.log(allResults.value);
    console.log("unique filters: ",uniqueFilters.value);
})

</script>
<template>
    <div class="grid grid-rows-[10%_1fr] h-full">

        <div class="h-screen grid grid-cols-[50%_50%] md:grid-cols-[30%_70%] sm:grid-cols-[40%_60%] transform transition-all duration-400">
            
            <div class="flex flex-col h-fit sm:pr-10 sm:pl-10 md:pr-10 md:pl-10 transform transition-all duration-400">
                    
                    <span class="self-center m-2 text-[1.1rem]">Фильтры</span>
                    
                    <div class="flex flex-col flex-wrap p-5 gap-1 rounded-lg ring ring-default shadow-lg">

                        <UInput v-model="filter.searchFilter" color='info' class='transform transition-all duration-400 w-full' icon="i-lucide-search" size="md" variant="outline" placeholder="Поиск..." />

                        <div class="flex">
                            <UDropdownMenu :items="modes">
                                <UButton icon="i-lucide-menu" size="sm" class="flex-0 self-center" color="neutral" variant="outline"/>
                            </UDropdownMenu >
                            <span class="ml-2 mt-4 mb-4">{{ searchType === "all" ? 'Всё' : searchType === "models" ? "Модели" : searchType === "datasets" ? "Датасеты" : "" }}</span>
                        </div>
                        
                        <span class="mt-4 mb-4">Теги</span>
                        <div class="flex lg:flex-row sm:flex-col gap-2 flex-wrap">
                            <UButton
                                v-for="tag in uniqueFilters.tags"
                                variant="outline" 
                                :color="filter.tags.has((tag as string).toLowerCase().trim()) ? 'success' : 'info'"
                                size="sm"
                                class="flex w-fit"
                                @click="toggleMethodButton"
                            >
                            {{ tag as string }}
                            </UButton>
                        </div>
                        <span class="mt-4 mb-4">Библиотеки</span>
                    <div class="flex gap-2 flex-wrap">
                        <div v-for="lib in uniqueFilters.library_name">
                        
                            <UButton v-if="(lib as string) == 'tensorflow'"
                                variant="outline" 
                                :color="filter.library_name.has((lib as string).toLowerCase().trim()) ? 'success' : 'info'"
                                size="sm"
                                class="flex"
                            >
                                <SiTensorflow class="w-4 h-4" />
                                TensorFlow
                            </UButton>
                        
                            <UButton v-else-if="lib == 'pytorch'"
                                variant="outline" 
                                :color="filter.library_name.has((lib as string).toLowerCase().trim()) ? 'success' : 'info'"
                                size="sm"
                                class="flex"
                                @click="toggleLibraryButton"
                            >
                                <SiPytorch class="w-4 h-4" />
                                PyTorch
                            </UButton>

                            <UButton v-else-if="lib == 'transformers' || lib == 'sentence-transformers'"
                                variant="outline" 
                                :color="filter.library_name.has((lib as string).toLowerCase().trim()) ? 'success' : 'info'"
                                size="sm"
                                class="flex"
                                @click="toggleLibraryButton"
                            >
                                <img alt="Hugging Face's logo" class="w-4 h-4" src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg">
                                {{ lib }}
                            </UButton>

                            <UButton v-else
                                variant="outline" 
                                :color="filter.library_name.has((lib as string).toLowerCase().trim()) ? 'success' : 'info'"
                                size="sm"
                                class="flex"
                                @click="toggleLibraryButton"
                            >
                                {{ lib }}
                            </UButton>
                        </div>
                    </div>
                    <div class="flex flex-col gap-2">
                        <span class="mt-4 mb-4">Локализация</span>
                        <div class="flex gap-2 flex-wrap">
                            <UButton
                            v-for="lang in uniqueFilters.language" 
                            variant="soft" 
                            :color="filter.language.has(lang as string) ? 'success' : 'info'"
                            size="sm"
                            class="flex"
                            @click="toggleLangButton"
                            >{{ ISO6391.getName(lang as string) }}</UButton>
                        </div>
                    </div>
                    </div>
            </div>

<VList :data="currentData" class="flex h-full overflow-auto p-3 ring ring-default shadow-sm" #default="{ item, index }">
    
    <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-auto w-full mb-3">
                <div class="flex flex-row">
                    <div class="flex flex-row gap-4">
                        <UIcon v-if='item["type"] == "datasets"' name="i-lucide-library" class="size-5" />
                        <UIcon v-if='item["type"] == "models"' name="i-lucide-astroid" class="size-5" />
                        <ULink v-if='item["type"] == "datasets"' as="button" :to="'/dataset/' + item['name']" class="flex self-center">
                            <span>
                                <template v-for="(part, idx) in highlightMatch(item.name, filter.searchFilter)" :key="idx">
                                    <span v-if="part.highlight" class="marker">{{ part.text }}</span>
                                    <span v-else>{{ part.text }}</span>
                                </template>
                            </span>
                        </ULink>
                        <ULink v-if='item["type"] == "models"' as="button" class="flex self-center">
                            <span>
                                <template v-for="(part, idx) in highlightMatch(item.name, filter.searchFilter)" :key="idx">
                                    <span v-if="part.highlight" class="marker">{{ part.text }}</span>
                                    <span v-else>{{ part.text }}</span>
                                </template>
                            </span>
                        </ULink>
                        <div v-if="item['type'] == 'datasets'" v-for="tag in item['task_categories']">
                            <div class="flex flex-row p-1 self-center rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="flex font-bold self-center text-xs">{{ tag }}</span>
                            </div>
                        </div>
                        <div v-if="item['library_name']?.toLowerCase() == 'transformers'" class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                            <UTooltip arrow :text="item['library_name']">
                                <img alt="Hugging Face's logo" class="w-4 h-4" src="https://huggingface.co/front/assets/huggingface_logo-noborder.svg">
                            </UTooltip>
                        </div>
                        <div v-else-if="item['library_name']?.toLowerCase() == 'sentence-transformers'" class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                            <UTooltip arrow :text="item['library_name']">
                                <svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1em" height="1em" role="img" aria-hidden="true" focusable="false" preserveAspectRatio="xMidYMid meet" viewBox="0 0 12 12" class="text-black inline-block text-sm "><g clip-path="url(#a)"><path d="M11.268.731A.556.556 0 1 1 10.156.73a.556.556 0 0 1 1.112.001ZM9.404 10.586a.556.556 0 1 1-1.111 0 .556.556 0 0 1 1.111 0Z" fill="#8AC9FE"></path><path d="M11.268 2.97a.556.556 0 1 1-1.112 0 .556.556 0 0 1 1.112 0ZM6.775 11.269a.555.555 0 1 1-1.11 0 .555.555 0 0 1 1.11 0ZM11.03 8.993A.556.556 0 1 1 9.92 8.99a.556.556 0 0 1 1.111.002Z" fill="#FDB441"></path><path d="M1.843 7.373a.555.555 0 1 1-1.11-.002.555.555 0 0 1 1.11.002Z" fill="#8AC9FE"></path><path d="M4.083 4.458a.556.556 0 1 1-1.112-.002.556.556 0 0 1 1.112.002ZM4.083 7.373a.555.555 0 1 1-1.11-.002.555.555 0 0 1 1.11.002ZM9.494 4.458a.556.556 0 1 1-1.112-.002.556.556 0 0 1 1.112.002ZM9.494 7.373a.555.555 0 1 1-1.11-.002.555.555 0 0 1 1.11.002ZM6.775 2.754a.555.555 0 1 1-1.11 0 .555.555 0 0 1 1.11 0ZM6.775 9.03a.555.555 0 1 1-1.11 0 .555.555 0 0 1 1.11 0Z" fill="#EE6161"></path><path d="M11.268.731a.556.556 0 0 1-1.073.202.555.555 0 0 0 .607-.75.555.555 0 0 1 .466.548ZM9.242 10.979a.555.555 0 0 1-.91-.192.553.553 0 0 0 .606-.748.555.555 0 0 1 .303.94Z" fill="#60B7FF"></path><path d="M11.268 2.97a.556.556 0 0 1-1.073.201.555.555 0 0 0 .607-.749.555.555 0 0 1 .466.549ZM6.775 11.269a.555.555 0 0 1-1.072.202.556.556 0 0 0 .606-.75.555.555 0 0 1 .466.548ZM10.868 9.385a.555.555 0 0 1-.91-.19.558.558 0 0 0 .607-.75.555.555 0 0 1 .303.94Z" fill="#FEA613"></path><path d="M1.843 7.373a.555.555 0 0 1-1.072.2.556.556 0 0 0 .606-.749.555.555 0 0 1 .466.549Z" fill="#60B7FF"></path><path d="M4.083 4.458a.556.556 0 0 1-1.073.2.555.555 0 0 0 .606-.749.555.555 0 0 1 .467.549ZM4.083 7.373a.555.555 0 0 1-1.073.2.556.556 0 0 0 .606-.75.558.558 0 0 1 .467.55ZM9.494 4.458a.556.556 0 0 1-1.073.2.555.555 0 0 0 .606-.749.555.555 0 0 1 .467.549ZM9.494 7.373a.555.555 0 0 1-1.073.2.556.556 0 0 0 .606-.75.558.558 0 0 1 .467.55ZM6.775 2.754a.555.555 0 0 1-1.072.2.556.556 0 0 0 .606-.749.554.554 0 0 1 .466.549ZM6.775 9.03a.555.555 0 0 1-1.072.201.556.556 0 0 0 .606-.75.555.555 0 0 1 .466.548Z" fill="#E94444"></path><path d="M10.888 2.262V1.44a.732.732 0 0 0 .555-.709.732.732 0 0 0-1.462 0c0 .343.238.63.556.709v.822a.73.73 0 0 0-.485 1.02l-.717.562a.734.734 0 0 0-.726-.038l-1.666-.942a.732.732 0 0 0-.724-.84.73.73 0 0 0-.721.84l-.544.306a.177.177 0 0 0 .088.33c.03 0 .059-.008.085-.024l.507-.287a.733.733 0 0 0 1.172 0l1.525.863a.728.728 0 0 0 .432 1.115v1.495a.734.734 0 0 0-.453 1.081l-1.504.85a.729.729 0 0 0-1.172 0l-1.484-.84a.734.734 0 0 0-.447-1.091V5.167a.732.732 0 0 0 .425-1.125l.293-.166a.177.177 0 0 0 .067-.24.177.177 0 0 0-.24-.066l-.404.228a.732.732 0 1 0-.492 1.368v1.496a.734.734 0 0 0-.534.535h-.821a.73.73 0 1 0 0 .351h.821a.73.73 0 0 0 1.068.46l1.612.911a.73.73 0 0 0 .546.819v.822a.73.73 0 1 0 .352 0v-.822a.73.73 0 0 0 .547-.819l1.625-.918a.724.724 0 0 0 .693.026l.589.588a.736.736 0 0 0 0 .756l-.604.602a.733.733 0 0 0-.914.096.732.732 0 0 0 .517 1.247.732.732 0 0 0 .637-1.087l.611-.61a.728.728 0 0 0 1.033-.3.175.175 0 0 0-.08-.236.175.175 0 0 0-.235.078.377.377 0 0 1-.608.1.38.38 0 0 1 .464-.594.174.174 0 0 0 .242-.058.177.177 0 0 0-.059-.242.727.727 0 0 0-.755 0L9.53 7.8a.734.734 0 0 0-.416-1.138V5.166a.732.732 0 0 0 .463-1.064l.697-.547a.732.732 0 0 0 1.169-.584.73.73 0 0 0-.555-.71Zm-4.668.871a.381.381 0 0 1-.38-.38.38.38 0 1 1 .38.38ZM3.148 4.458a.38.38 0 1 1 .759 0 .38.38 0 0 1-.76 0Zm-1.86 3.294a.38.38 0 1 1 0-.759.38.38 0 0 1 0 .759Zm1.86-.38a.38.38 0 0 1 .759 0c0 .206-.175.38-.38.38a.38.38 0 0 1-.38-.38Zm3.451 3.897a.38.38 0 1 1-.759 0 .38.38 0 0 1 .76 0Zm-.38-1.86a.38.38 0 0 1-.379-.38.38.38 0 1 1 .38.38Zm2.898 1.445a.38.38 0 1 1-.536-.536.38.38 0 0 1 .536.537ZM10.333.732a.38.38 0 1 1 .759 0 .38.38 0 0 1-.759 0ZM9.318 7.373c0 .203-.174.379-.38.379a.38.38 0 1 1 .38-.38Zm-.38-2.536a.38.38 0 1 1 0-.759.38.38 0 0 1 0 .759Zm1.774-1.487a.38.38 0 1 1 0-.759.38.38 0 0 1 0 .76Z" fill="currentColor"></path></g><defs><clipPath id="a"><path fill="currentColor" d="M0 0h12v12H0z"></path></clipPath></defs></svg>
                            </UTooltip>
                        </div>
                        <div v-else-if="item['library_name']?.toLowerCase() == 'pytorch'" class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                            <UTooltip arrow :text="item['library_name']">
                                <UTooltip arrow :text="item['library_name']">
                                    <SiPytorch class="h-4 self-center" />
                                </UTooltip>
                            </UTooltip>
                        </div>
                        <div v-else-if="item['library_name']?.toLowerCase() == 'tensorflow'" class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                            <UTooltip arrow :text="item['library_name']">
                                <UTooltip arrow :text="item['library_name']">
                                    <SiTensorflow class="h-4 self-center" />
                                </UTooltip>
                            </UTooltip>
                        </div>
                        <div v-else-if="item['library_name'] !== null && item['library_name'] !== undefined" class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                            <span class="text-xs">{{ item['library_name'] }}</span>
                        </div>
                        <UDropdownMenu v-if="item['language']"
                            arrow 
                            size="xs" 
                            :items="languageItems(item['language'] ?? '')"
                            :ui="{ content: 'min-w-fit', item: 'whitespace-nowrap' }"
                            >
                                <UButton variant="outline" size="xs">
                                    Языки
                                </UButton>
                        </UDropdownMenu>
                    </div>
                </div>
                <div class="h-full w-full flex flex-col">
                    <div class="flex items-center text-center gap-2 mb-2">
                        <GrLicense class="flex w-4 h-4"/>
                        <span class="flex text-center text-md">{{ Array.isArray(item['license']) ? item['license'][0] : item['license'] }}</span>
                    </div>
                    <div class="flex flex-wrap gap-2">
                        <UBadge v-for="tag in item['tags']" color="neutral" variant="outline" :label="tag"/>
                    </div>
                </div>
            </div>

            </VList>

        </div>
    </div>
</template>