<script setup lang="ts">

import { ref, onMounted, onUnmounted, h } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate';
import { toast } from 'vue-sonner';
import { editor, type collapsible } from '#build/ui';
import type { ContextMenuItem, TreeItem } from '@nuxt/ui';
import { CodeEditor } from 'monaco-editor-vue3';

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
const items = ref<TreeItem[]>();

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

    <CodeEditor
        v-model:value="textarea_value"
        language="javascript"
        theme="vs-dark"
        :options="editorOptions"
    />
    
    </div>
  </div>
</template>