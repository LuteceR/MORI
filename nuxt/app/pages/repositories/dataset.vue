<script setup lang="ts">

import { ref, onMounted, onUnmounted, h } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate';
import { toast } from 'vue-sonner';
import { chatPromptSubmit, editor, type collapsible } from '#build/ui';
import type { ContextMenuItem, TreeItem } from '@nuxt/ui';
import { CodeEditor } from 'monaco-editor-vue3';
import Papa from 'papaparse';
import type { DropdownMenuItem } from '@nuxt/ui'
import { object } from 'zod';

type DatasetResponse = {
    dataset: string,
    tree: TreeItem[]
}

const editorOptions = {
  fontSize: 14,
  minimap: { enabled: false },
  automaticLayout: true
};

const repo_id_header = ref("Датасет");
const repo_id = ref("");
const openSidebar = ref(true);
const loading = ref(false);
const textarea_value = ref("");
const table_content = ref({});
const items = ref<TreeItem[]>();
const items_data = ref<DropdownMenuItem[]>([]);
const items_data_marks = ref<DropdownMenuItem[]>([]);
const jsons_data_for_marks = ref([]);
const arr_words = ref([]);
const arr_marks = ref([]);
const openCM = ref(false);

function RightClick(event: MouseEvent) {
    const el = event.target as HTMLElement;
    el.style.background = "green";
    openCM.value = true;
    // console.log(el)
}

function processingWords(name: String) {
    for (const item of jsons_data_for_marks.value) {
        if (typeof item[name] == "string") {
            arr_words.value.push(item[name]);
        } else {
            arr_words.value.push(Object.values(item[name]))
        }
    }
}

function processingMarks(name: String) {
    console.log(name);
}

function processingTreeItems(tree: TreeItem[], path = ""): TreeItem[] {
    return tree.map((item) => {

        var currentPath = path
        ? `${path}`
        : "";
        
        if (item.children) {
            return {
                ...item,
                children: processingTreeItems(item.children, currentPath += item.label +  "/")
            }
        
        } else {
            if (item.label?.endsWith("json") || item.label?.endsWith("jsonl")) {
                item.icon = 'i-vscode-icons-file-type-json'
            } else {
                item.icon = 'i-lucide-file'
            }
            return {
                ...item,
                onSelect: async() => {
                    try {

                        if (currentPath) {
                            currentPath += "/";
                        }

                        const response = await $fetch.raw(
                            "http://localhost:8000/file_from_dataset",
                            {
                                method: "GET",
                                query: {
                                    dataset: repo_id.value,
                                    filepath: currentPath + item.label,
                                }
                            }
                        )
                        
                        // вывод текста в эдитор
                        textarea_value.value = response._data?.value;
                        arr_words.value = [];
                        // получение разделов в json/jsonl
                        try {
                            jsons_data_for_marks.value = (response._data?.value ?? "")
                                .trim()
                                .split('\n')
                                .map(line => JSON.parse(line));
                            const keys = Object.keys(jsons_data_for_marks.value[0]); 
                            items_data.value = keys.map(e => ({
                                label: e,
                                onSelect(event: Event) {
                                    arr_words.value = []
                                    processingWords(e)
                                }
                            }))

                            items_data_marks.value = keys.map(e => ({
                                label: e,
                                onSelect(event: Event) {
                                    processingMarks(e)
                                }
                            }))
                            // console.log(items_data.value)
                        } catch (e) {
                            items_data.value = [{
                                label : "Нет"
                            }]
                            return null;
                        }

                        // перевод в json
                        if (item.label!.slice(-3) == "csv") {
                            let data = Papa.parse(textarea_value.value, {
                                    header: true,
                                    delimiter: ',',
                                })
                            table_content.value = data.data
                            console.log(data.data)
                        }

                    } catch(e) {
                        console.log(e)
                        // console.log(currentPath + item.label)
                    }
                }
            }
        }
    })
}

async function request() {
    if (repo_id.value == "") return

    loading.value = true;
    
    try {
        const response = await $fetch.raw<DatasetResponse>("http://localhost:8000/dataset", {
            method: 'GET',
            query:  {
                dataset: repo_id.value
            }
        })

        repo_id_header.value = response._data?.dataset!;
        // tree.value = response._data?.tree ?? {}
        items.value = response._data!.tree
        // console.log(response._data?.tree)
        // const uiTree = convertTree(response._data!.tree)

        // console.log(tree.value);
    } catch (e) {
        console.log(e);
        loading.value = false;
    }

    items.value = processingTreeItems(items.value!)
    loading.value = false;
};

const b = ref(false);
const i = ref(false);
const o = ref(false);

const tabs = [
    {
        label: 'editor',
        slot: 'editor',
    },
    {
        label: "studio",
        slot: "studio",
    },
    {
        label: 'marks',
        slot: 'marks',
    },
]

const state = reactive({
    editor: textarea_value,
    studio: table_content,
    marks: 'marks',
})

const contextMenuMarks = computed<ContextMenuItem[]>(() => [{
        label: "метки",
        type: 'label' as const,
    }, {
        type: 'separator' as const
    }, {
        label:"b",
        type: 'checkbox' as const,
        checked: b.value,
        onUpdateChecked(checked: boolean) {
            b.value = checked
        }
    }, {
        label: "i",
        type: 'checkbox' as const,
        checked: i.value,
        onUpdateChecked(checked: boolean) {
            i.value = checked
        },
    }, 
    {
    label: "o",
    type: 'checkbox' as const,
    checked: o.value,
    onUpdateChecked(checked: boolean) {
        o.value = checked
    },
}])

</script>

<template>
  <div
    class="flex flex-1">
    <USidebar
      v-model:open="openSidebar"
      variant="inset"
      collapsible="offcanvas"
      side="left"
      :ui="{
          gap: 'h-[calc(100%-var(--ui-header-height))]',
          container:
            'absolute top-(--ui-header-height) bottom-0 h-[calc(100%-var(--ui-header-height))]'
        }"
    >
        <template #header>
            <UIcon name="i-lucide-database" class="size-6" />
            <UUser v-if="!loading" :name="repo_id_header" size="xl" />
            <USkeleton v-if="loading" class="h-6 w-45" />
        </template>

        <h1 class="">Файлы</h1>
        <USeparator />

        <UTree
            :items="items"
            orientation="vertical"
            :ui="{ 
                link: 'p-1.5 overflow-hidden',
                listWithChildren: 'ml-3',
            }"
        />
    </USidebar>

    <div
        class="flex-1 flex flex-col overflow-hidden h-[91vh]
        lg:peer-data-[variant=floating]:my-4 peer-data-[variant=inset]:m-4 
        lg:peer-data-[variant=inset]:not-peer-data-[collapsible=offcanvas]:ms-0 
        peer-data-[variant=inset]:rounded-xl peer-data-[variant=inset]:shadow-sm 
        peer-data-[variant=inset]:ring peer-data-[variant=inset]:ring-default bg-default"
    >

    
    <UContainer
    class="h-(--ui-header-height) shrink-0 flex items-center px-4 border-b border-default transform transition-all duration-200"
    >
    
    
        <UButton
            icon="i-lucide-panel-right"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            @click="openSidebar = !openSidebar"
        />
        
        <UInput
            v-model="repo_id"
            color="neutral" 
            variant="subtle"
            size="lg"
            class="w-50 sm:ml-10 ml-2 transform transition-all duration-200"
            placeholder="user/dataset"
            @keydown.enter="request"
            />
            
    </UContainer>
        
        <UTabs 
        :items="tabs" 
        class="flex flex-1 h-full"
        variant="link"
        :ui="{
            content: 'h-full'
        }"
        >

            <template #editor>
                <CodeEditor
                v-model:value="state.editor"
                language="javascript"
                theme="vs-dark"
                :options="editorOptions"
                class="flex h-full"
                />
            </template>

            <template #studio>
                <UTable
                :data="table_content"
                class="flex h-full w-full"
                :ui="{
                    td: 'max-w-fit whitespace-normal break-words'
                }"
                />
            </template>

            <template #marks>
                <div class="flex flex-row">
                    <UDropdownMenu
                    arrow
                    :items="items_data"
                    :ui="{
                        content: 'w-4'
                    }"
                    >
                        <UButton
                        label="Данные" 
                        icon="i-lucide-braces" 
                        color="neutral" 
                        variant="outline"
                        class="flex ml-2" />
                    </UDropdownMenu>

                    <UDropdownMenu
                    arrow
                    :items="items_data_marks"
                    :ui="{
                        content: 'w-4'
                    }"
                    >
                        <UButton
                        label="Метки" 
                        icon="i-lucide-braces" 
                        color="neutral" 
                        variant="outline"
                        class="flex ml-2" />
                    </UDropdownMenu>
                </div>
            <USeparator class="mt-2"/>
            <p class="">
                <UContextMenu :items="contextMenuMarks">
                    <span class="text-green-500">sadsa</span>
                </UContextMenu>
            </p>
                <div class="flex flex-wrap overflow-y-auto gap-6 p-3 h-full whitespace-normal break-words">
                    <UContextMenu
                        :items="contextMenuMarks"
                        v-model:open="openCM"
                    >
                    <div>
                        <p class="flex flex-wrap gap-1" v-for="text in arr_words">
                            <span v-for="word in text"
                            @contextmenu.capture="RightClick($event)">
                            {{ word }}
                        </span>
                    </p>
                    </div>
                    </UContextMenu>
                </div>
            </template>
        </Utabs>
    
    </div>
  </div>
</template>