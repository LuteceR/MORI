<script setup lang="ts">

import { ref, onMounted, onUnmounted, h } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate';
import { toast } from 'vue-sonner';
import { chatPromptSubmit, commandPalette, editor, type collapsible } from '#build/ui';
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
  automaticLayout: true,
};

const repo_id_header = ref("Датасет");
const repo_id = ref("");
const openSidebar = ref(true);
const loading = ref(false);
const textarea_value = ref("");
const table_content = ref({});
const items = ref<TreeItem[]>();
const items_data = ref<DropdownMenuItem[]>([{
                                        label : "Нет"
                                    }]);
const items_data_marks = ref<DropdownMenuItem[]>([{
                                        label: "Нет"
                                    }]);
const textareaJsons = ref<string[]>([]);
const arr_words = ref<string[]>([]);
const arr_marks = ref<string[][]>([]);
const current_arr_marks = ref<string[][]>([]);
const openCM = ref(false);
const pageNum = ref(1);
const pageSize = 20;
const tab = ref();
const IsPaginator = ref(false);
let reader: ReadableStreamDefaultReader | null = null;
const toast = useToast();
const editorLanguage = ref('json');
const openSidebarMarks = ref(false);
const openedFile = ref('');
const eventTarget = ref<HTMLElement | null>(null);

const colors = [
    // B marks
    ["red", "orange", "amber", 
    "yellow", "lime", "green", 
    "emerald", "teal", "cyan",
    "sky", "blue"],
    // I marks
    ["indigo", "violet", "purple", 
    "fuchsia", "pink", "rose",
    "slate", "olive", "mist", 
    "mauve", "zinc"]

]

const colorDepths = [
    500, 700, 900
]

const allColors = colors.flatMap(group =>
  group.flatMap(color =>
    colorDepths.map(depth => `${color}-${depth}`)
  )
)

const BColors = allColors.slice(0, allColors.length / 2)
const IColors = allColors.slice(allColors.length / 2)

const dictOfMarksAndBG = ref(new Map<string, string>());
dictOfMarksAndBG.value.set("B", `bg-sky-500/50 rounded-sm`);
dictOfMarksAndBG.value.set("I", `bg-indigo-500/50 rounded-sm`);
dictOfMarksAndBG.value.set("O", `bg-stone-500/50 rounded-sm`);

const classMatrix = computed(() =>
  current_arr_marks.value.map(row =>
    row.map(mark =>  dictOfMarksAndBG.value.get(mark) ?? '')
  )
);

watch(tab, (newTab, oldTab) => {
    if (newTab == '2') {IsPaginator.value = true}
    else {IsPaginator.value = false};
})

// подсчитывание строк для одной странице
const paginated = computed(() => {
    const start = (pageNum.value - 1) * pageSize
    // console.log(start, start + pageSize);
    current_arr_marks.value = arr_marks.value.slice(start, start + pageSize);
    // console.log(arr_marks.value.slice(start, start + pageSize))
    return arr_words.value?.slice(start, start + pageSize)
})

const saveChanges = async (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
        e.preventDefault();
        
        if (repo_id.value == "") {
            toast.add({
                    color: "error",
                    title: "Не выбран датасет",
                    icon: 'i-lucide-ban',
                    ui: {
                        description: 'whitespace-pre-line'
                    }
                })  
            return;
        }
        if (openedFile.value == "") {
            toast.add({
                    color: "error",
                    title: "Не выбран файл",
                    icon: 'i-lucide-ban',
                    ui: {
                        description: 'whitespace-pre-line'
                    }
                })  
            return;
        }

        await fetch(
            "http://127.0.0.1:8000/save_file_changes", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                dataset: repo_id.value,
                filename: openedFile.value,
                content: textarea_value.value,
            }),
        }).then((response) => {
            // console.log(response)
            if (response.status != 200) {
                toast.add({
                    color: "error",
                    title: "Произошла ошибка!",
                    description: `Статус: ${response.status}\n${response.statusText}`,
                    icon: 'i-lucide-ban',
                    ui: {
                        description: 'whitespace-pre-line'
                    }
                })        
            }
            if (response.status == 200) {
                toast.add({
                    color: "success",
                    title: "Изменения сохранены!",
                    icon: 'i-lucide-save',
                })
            }
        });

    }
}

// подгрузка тегов выбранного слова
function RightClick(e : MouseEvent, i : number, k : number) {
    eventTarget.value = e.target as HTMLElement;
    const elMarks = arr_marks?.value?.[i]?.[k]?.split("-");
    // console.log(current_arr_marks.value[el.dataset.i][el.dataset.k].split("-"))

    if (elMarks.length == 3) {
        value1.value = elMarks[0];
        value2.value = elMarks[1];
        value3.value = elMarks[2];
    } 
    if (elMarks.length == 2) {
        if (elMarks[1] in itemsSMC.value) {
            value1.value = elMarks[0];
            value2.value = elMarks[1];
            value3.value = '';
        } else {
            value1.value = elMarks[0];
            value2.value = '';
            value3.value = elMarks[1];
        }
    }
    if (elMarks.length == 1) {
        value1.value = elMarks[0];
        value2.value = null;
        value3.value = null;
    }
}

// Добавление нового тега и замена старого в датасете
function updateValue(event, array : string[]) {
    // console.log((event.target as HTMLElement).value);
    // console.log(eventTarget.value?.dataset.i);
    const i = eventTarget.value?.dataset.i;
    const k = eventTarget.value?.dataset.k;
    console.log(arr_marks.value[i][k]);

    const parts = arr_marks.value[i][k].split("-");

    parts[0] = value1npVal.value || parts[0];
    parts[1] = value2npVal.value || parts[1];
    parts[2] = value3npVal.value || parts[2];

    const set = new Set(arr_marks.value.flat());
    const part = parts.filter(item => item !== undefined).join("-");

    if ([...set].includes(part)) {
        toast.add({
            color: "error",
            title: "Данная метка уже существует",
            ui: {
                description: 'whitespace-pre-line'
            }
        });
        
        return;
    } else {
        array.push((event.target as HTMLElement).value);
        arr_marks.value[i][k] = part;
        dictOfMarksAndBG.value.set(part, "bg-pink-300/50 rounded-sm")
        // console.log(i, k);
        // console.log(arr_marks.value);
    }
}

// подгрузка слов из выбранного ключа в датасете json/jsonl, csv
function printingWords(nameWords: String) {
    // отображение слов
    for (const jsonString of textareaJsons.value) {
        const json = JSON.parse(jsonString);
        arr_words.value.push(json[nameWords]);
    }
}

// добавление меток из выбранного ключа в датасете json/jsoinl, csv
function retrievingMarks(nameMarks: String) {
    // добавление в массив с метками
    for (const jsonString of textareaJsons.value) {
        const json = JSON.parse(jsonString);
        arr_marks.value.push(json[nameMarks]);
    }
    
    const set = new Set(arr_marks.value.flat())
    const unique = [...set]
    for (var i = 0; i < unique.length; i++) {
        
        if (!dictOfMarksAndBG.value.has(unique[i])) {
            
            // console.log(`unique[${i}][0] = ${unique[i][0]}`)
            if (unique[i][0] == "B") {
                dictOfMarksAndBG.value.set(unique[i], `bg-${BColors[i]}/50 rounded-sm`);
            }

            if (unique[i][0] == "I") {
                dictOfMarksAndBG.value.set(unique[i], `bg-${IColors[i]}/50 rounded-sm`);
            }
        }
    }
    
    // console.log(`unique: ${unique.length}`)
    // console.log(dictOfMarksAndBG.value);
    // console.log(arr_marks);
}

// преобразование текста json/jsonl, csv для получение доступных полей в датасете
function processingMarks(filename: String) {
    if(filename.includes(".json") || filename.includes(".jsonl")) {
        
        if (filename.includes(".jsonl")) {
            textareaJsons.value = textarea_value.value.split("\n");
            const first = JSON.parse(textareaJsons.value[0]!);
            
            // обновление значений в выборе ключа хранения данных для меток и самих меток

            items_data.value = Object.keys(first).map(e => ({
                label: e,
                onSelect(event: Event) {
                    arr_words.value = [];
                    printingWords(e);
                }
            }));
            items_data_marks.value = Object.keys(first).map(e => ({
                label: e,
                onSelect(event: Event) {
                    arr_marks.value = [];
                    retrievingMarks(e);
                }
            }));
        }
    }

    if(filename.includes(".csv")) {

        try {
            const result = Papa.parse(textarea_value.value, {
                header: true,
                skipEmptyLines: true
            });

            const keys = Object.keys(result.data[0]);
            
            // !!!
            // если здесь всё красное, то это TS ругается на невозможность получения данных сервера из-за CORS политики
            // !!!

            items_data.value = keys.map(e => ({
                label: e,
                onSelect(event: Event) {
                    arr_words.value = []
                    processingWords(e)
                }
            }));
        
            items_data_marks.value = keys.map(e => ({
                label: e,
                onSelect(event: Event) {
                    processingMarks(e)
                }
            }));

        } catch (e) {
            items_data.value = [{
                label : "Нет"
            }]
            
            items_data_marks.value = [{
                label: "Нет"
            }]
            
            console.log(e);
            return null;
        }
    }
}

// создание таблицы в слоте "студия"
function processingTable(filename: string) {
    if (filename.includes(".csv")) {
        // console.log(item.label?.slice(-3));
        let data = Papa.parse(textarea_value.value, {
            header: true,
            delimiter: ',',
        })
        table_content.value = data.data
    }
    table_content.value = []
}

// создание Utabs древа файлов датасета
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
                    openedFile.value = item.label!;
                    
                    if (reader) {
                        reader.cancel();
                        reader = null;
                    }

                    items_data.value = [{
                        label : "Нет"
                    }]
                    
                    items_data_marks.value = [{
                        label: "Нет"
                    }]

                    // язык не изменяется - починить
                    if (item.label!.includes(".md ")) {
                        editorLanguage.value = "markdown";
                    }
                    if (item.label!.includes(".js ") || item.label!.includes(".ts ")) {
                        console.log("js | ts");
                        editorLanguage.value = "javascript";
                    }
                    if (item.label!.includes(".json ") || item.label!.includes(".jsonl ")) {
                        console.log("json | jsonl");
                        editorLanguage.value = "json";
                    }
                    if (item.label!.includes(".py ")) {
                        console.log("py");
                        editorLanguage.value = "python";
                    }

                    textarea_value.value = "";
                    arr_words.value = [];

                    try {
                        if (currentPath) {
                            currentPath += "/";
                        }
                        
                        // console.log(item.label);
                        
                        fetch(
                            "http://localhost:8000/file_from_dataset?" +
                            new URLSearchParams(
                            {
                                dataset: repo_id.value,
                                filepath: currentPath + item.label,
                            })
                        ).then((response) => {
                            reader = response.body!.getReader();
                            const decoder = new TextDecoder();
                            
                            // чтение чанков потокового ответа
                            reader?.read().then(function processText({ done, value }) {
                                if (done) {
                                    processingMarks(item.label!);
                                    processingTable(item.label!);
                                    
                                    toast.add({
                                        title: "Файл полностью загружен!",
                                        icon: 'i-lucide-wifi',
                                    })
                                    return;
                                }
                                
                                const val = decoder.decode(value, { stream : true });
                                textarea_value.value += val;
                                return reader?.read().then(processText);
                            });
                        })
                        
                    } catch(e) {
                        console.log(e)
                    }
                }
            }

        }
    })
}

const RepoError = ref<string | null>(null);

async function request() {
    if (repo_id.value == "") return

    loading.value = true;
    
    try {
        const response = await $fetch<DatasetResponse>("http://localhost:8000/dataset", {
            method: 'GET',
            query:  {
                dataset: repo_id.value
            }
        })

        // tree.value = response._data?.tree ?? {}
        if (response.dataset == undefined) {
            RepoError.value = "Некорректное repo id";
            loading.value = false;
            console.log(response)
            return;
        }
        RepoError.value = null;
        // console.log(response._data?.tree)
        // const uiTree = convertTree(response._data!.tree)
        
        repo_id_header.value = response.dataset!;
        items.value = response.tree;
        
        // console.log(tree.value);
    } catch (e) {
        console.log(e);
        loading.value = false;
        return;
    }
    
    // console.log(items.value);
    items.value = processingTreeItems(items.value!)
    loading.value = false;
};

const b = ref(false);
const i = ref(false);
const o = ref(false);

const tabs = [
    {
        label: 'эдитор',
        slot: 'editor',
    },
    {
        label: 'студия',
        slot: 'studio',
    },
    {
        label: 'метки',
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
    }
])

const value1 = ref('');
const value2 = ref('');
const value3 = ref('');

const value1npVal = ref('');
const value2npVal = ref('');
const value3npVal = ref('');

const value1Input = ref(false);
const value2Input = ref(false);
const value3Input = ref(false);

const itemsSMB = ref(['B', 'I', 'O'])
const itemsSMC = ref(['LEFT', 'LEG','RIGHT'])
const itemsSME = ref(['PER', 'ORG', 'LOC', 'FAC',
                      'GPE', 'DATE', 'MONEY', 'LAW',
                      'EVENT', 'PRODUCT', 'MISC'])

onMounted(() => {
    window.addEventListener('keydown', saveChanges);
})

onUnmounted(() => {
    window.removeEventListener('keydown', saveChanges);
})

</script>

<template>
    <!-- затычка :( -->
    <div class="bg-red-500/50 bg-red-700/50 bg-red-900/50 bg-orange-500/50 bg-orange-700/50 bg-orange-900/50 bg-amber-500/50 bg-amber-700/50 bg-amber-900/50 bg-yellow-500/50 bg-yellow-700/50 bg-yellow-900/50 bg-lime-500/50 bg-lime-700/50 bg-lime-900/50 bg-green-500/50 bg-green-700/50 bg-green-900/50 bg-emerald-500/50 bg-emerald-700/50 bg-emerald-900/50 bg-teal-500/50 bg-teal-700/50 bg-teal-900/50 bg-cyan-500/50 bg-cyan-700/50 bg-cyan-900/50 bg-sky-500/50 bg-sky-700/50 bg-sky-900/50 bg-blue-500/50 bg-blue-700/50 bg-blue-900/50 bg-indigo-500/50 bg-indigo-700/50 bg-indigo-900/50 bg-violet-500/50 bg-violet-700/50 bg-violet-900/50 bg-purple-500/50 bg-purple-700/50 bg-purple-900/50 bg-fuchsia-500/50 bg-fuchsia-700/50 bg-fuchsia-900/50 bg-pink-500/50 bg-pink-700/50 bg-pink-900/50 bg-rose-500/50 bg-rose-700/50 bg-rose-900/50 bg-slate-500/50 bg-slate-700/50 bg-slate-900/50 bg-olive-500/50 bg-olive-700/50 bg-olive-900/50 bg-mist-500/50 bg-mist-700/50 bg-mist-900/50 bg-mauve-500/50 bg-mauve-700/50 bg-mauve-900/50 bg-zinc-500/50 bg-zinc-700/50 bg-zinc-900/50
    "></div>
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
        class="flex-1 flex flex-col overflow-hidden h-[88vh] w-full
        lg:peer-data-[variant=floating]:my-4 peer-data-[variant=inset]:m-4 
        lg:peer-data-[variant=inset]:not-peer-data-[collapsible=offcanvas]:ms-0 
        peer-data-[variant=inset]:rounded-xl peer-data-[variant=inset]:shadow-sm 
        peer-data-[variant=inset]:ring peer-data-[variant=inset]:ring-default"
    >
    
    <UContainer
        class="w-full p-5 h-[calc(var(--ui-header-height)*1.4)]! items-center 
        max-w-none flex transform transition-all duration-200"
    >
    
        <UButton
            icon="i-lucide-panel-right"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            class="mb-auto flex"
            @click="openSidebar = !openSidebar"
        />
        
        <UFormField class=" sm:ml-10 mb-auto ml-2 self-center justify-center" :error="RepoError">
            <div class="flex flex-row">
                <UInput
                    v-model="repo_id"
                    color="neutral" 
                    variant="subtle"
                    size="lg"
                    class="w-50 transform transition-all duration-200"
                    placeholder="user/dataset"
                    @keydown.enter="request"
                />
                <!-- <span v-if='RepoError' class="text-error ml-2 self-center text-md">{{ RepoError }}</span> -->
            </div>
        </UFormField>
        
        <UButton
            v-if="IsPaginator"
            icon="i-lucide-palette"
            color="neutral"
            variant="ghost"
            aria-label="Toggle sidebar"
            class="ml-6 flex"
            @click="openSidebarMarks = !openSidebarMarks"
        />

        <UButton
            @click="saveChanges"
            label="Сохранить"
            color="success" 
            variant="subtle"
            :ui="{
                base:'ml-auto'
            }" 
        />
        <span class="ml-2 text-success/60">ctrl+s</span>
    </UContainer>
        
        <UTabs
            v-model:model-value="tab"
            :items="tabs"
            class="flex flex-1 h-full"
            variant="link"
            :ui="IsPaginator ? {
                content: 'h-full',
                list: 'border-none <- doesnt work :c'
            } : { 
                content: 'h-full',
            }"
        >

            <template #editor>
                <CodeEditor
                    v-model:value="state.editor"
                    :language="editorLanguage"
                    theme="vs-dark"
                    :options="editorOptions"
                    class="flex h-full"
                />
            </template>

            <template #studio>
                <UTable
                    :data?="table_content"
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
                            class="flex ml-2" 
                        />
                    </UDropdownMenu>

                </div>
            <USeparator class="mt-2"/>
                <div class="flex flex-wrap overflow-y-auto max-h-full gap-6 p-3 whitespace-normal break-words"
                >
                <UContextMenu
                    v-model:open="openCM"
                    :ui="{
                        content: 'rounded-lg ring ring-default shadow-lg'
                    }"
                    @update:open="value1Input = false; value2Input = false; value3Input = false"
                >
                        <template #content-bottom>
                            <div @contextmenu.prevent>
                                <p class="justify-center text-center pt-1">Метки</p>
                                <div class="flex flex-row p-1 gap-2">
                                    <UFieldGroup>
                                        <USelectMenu
                                            v-if="!value1Input"
                                            v-model="value1"
                                            color="primary" 
                                            class="w-14"
                                            :items="itemsSMB" 
                                            @click.stop 
                                        />
                                        <UInput
                                            color="success"
                                            class="w-14"
                                            v-model="value1npVal"
                                            v-if="value1Input"
                                            @keydown.enter="updateValue($event, itemsSMB)"
                                        />
                                        <UButton
                                            @click="value1Input = !value1Input; value1npVal = ''"
                                            color="success"
                                            size="sm"
                                            variant="subtle"
                                            icon="i-lucide-plus"
                                        />
                                    </UFieldGroup>
                                    <UFieldGroup>
                                        <USelectMenu 
                                            v-if="!value2Input"
                                            v-model="value2" 
                                            class='w-25' 
                                            :items="itemsSMC" 
                                            @click.stop 
                                        />
                                        <UInput
                                            v-model="value2npVal"
                                            color="success"
                                            class="w-25"
                                            v-if="value2Input"
                                            @keydown.enter="updateValue($event, itemsSMC)" 
                                        />
                                        <UButton
                                            @click="value2Input = !value2Input; value2npVal = ''"
                                            color="success"
                                            size="sm"
                                            variant="subtle"
                                            icon="i-lucide-plus"
                                        />
                                    </UFieldGroup>
                                    <UFieldGroup>
                                        <USelectMenu 
                                            v-if="!value3Input"
                                            v-model="value3" 
                                            class='w-35' 
                                            :items="itemsSME" 
                                            @click.stop 
                                        />
                                        <UInput 
                                            color="success"
                                            class="w-35"
                                            v-model="value3npVal"
                                            v-if="value3Input"
                                            @keydown.enter="updateValue($event, itemsSME)"
                                            />
                                            <UButton
                                            @click="value3Input = !value3Input; value3npVal = ''"
                                            color="success"
                                            size="sm"
                                            variant="subtle"
                                            icon="i-lucide-plus"
                                            />
                                    </UFieldGroup>
                                </div>
                            </div>
                        </template>
                    <div>
                        <p class="flex flex-wrap gap-2" v-for="(text, i) in paginated">
                            <span 
                                v-for="(word, k) in text"
                                :data-i="i"
                                :data-k="k"
                                :class="(classMatrix?.[i]?.[k] ?? '') + ' mt-1 pl-1 pr-1'"
                                @contextmenu.capture="RightClick($event, i, k)"
                            >
                            {{ word }}
                            </span>
                        </p>
                    </div>
                </UContextMenu>
                </div>
            </template>
        </Utabs>
    </div>

    <USidebar
        v-model:open="openSidebarMarks"
        variant="inset"
        title="Цвета тегов"
        collapsible="offcanvas"
        side="right"
        mode="slideover"
        :ui="{
            root: 'h-[20svh]',
            container:
                'flex flex-col mt-4 rounded-lg ring ring-default shadow-lg top-(--ui-header-height) bottom-0 h-[calc(80%-var(--ui-header-height))]'
            }"
        >

        <UBadge v-for="mark in dictOfMarksAndBG"
        class="text-gray font-medium"
        :label="mark[0]" 
        variant="soft" 
        :class="mark[1]" />

    </USidebar>

</div>
<UPagination
    v-if="IsPaginator"
    v-model:page="pageNum"
    :total="arr_words.length"
    :items-per-page="pageSize"
    variant="outline"
    active-variant="subtle"
    :sibling-count="2"
    :ui="{
        root: 'flex w-full justify-center'
    }"
/>
</template>