<script setup lang="ts">
definePageMeta({
    layout: {
        name: 'main',
    }
})

import { ref, onMounted, onUnmounted, h } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate';
import { toast } from 'vue-sonner';
import type { collapsible } from '#build/ui';
import type { ContextMenuItem, TreeItem } from '@nuxt/ui';

type DatasetResponse = {
    dataset: string,
    tree: TreeItem[]
}

const repo_id_header = ref("some");
const repo_id = ref("some");

const textarea_value = ref("");
const items = ref<TreeItem[]>()

// function processText(text: str) {

// }

function processingTreeItems(tree: TreeItem[], path = ""): TreeItem[] {
    return tree.map((item) => {

        var currentPath = path
        ? `${path}`
        : ""
        
        if (item.children) {
            return {
                ...item,
                children: processingTreeItems(item.children, currentPath += "\\\\" + item.label)
            }
        
        } else {
            return {
                ...item,
                onSelect: async() => {
                    try {

                        const response = await $fetch.raw(
                            "http://localhost:8000/file_from_dataset",
                            {
                                method: "GET",
                                query: {
                                    dataset: repo_id.value,
                                    filepath: currentPath + "\\"+ item.label,
                                }
                            }
                        )
                        
                        textarea_value.value = response._data?.value
                        // console.log(response)
                    } catch(e) {
                        console.log(e)
                    }
                }
            }
        }
    })
}

async function request() {
    if (repo_id.value == "") return

    try {
        const response = await $fetch.raw<DatasetResponse>("http://localhost:8000/dataset", {
            method: 'GET',
            query:  {
                dataset: repo_id.value
            }
        })

        repo_id_header.value = response._data?.dataset.replace("\\", "/") ?? "None"
        // tree.value = response._data?.tree ?? {}
        items.value = response._data!.tree!
        // const uiTree = convertTree(response._data!.tree)

        // console.log(tree.value);
    } catch (e) {
        console.log(e);
    }

    items.value = processingTreeItems(items.value!)
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
    <div class="flex container mt-10">
        <h1 class="font-mono text-2xl">
            {{ repo_id_header }}
        </h1>
        <UTextarea class="ml-22" v-model="repo_id" 
            :maxrows="1" 
            :rows="1" 
            placeholder="repo_id" 
            autoresize
            @change="request()" />
    </div>
    <div class="flex container">
        <UTree :items="items" />
    </div>
    <div class="flex ">
        <UContextMenu :items="contextMenuMarks"><span>Someword</span></UContextMenu>
    </div>
</template>