<script setup lang="ts">

import { gsap } from 'gsap';
import { SiTensorflow, SiPytorch } from 'vue-icons-plus/si';

const searchError = ref(false);

</script>
<template>
    <div class="flex w-full h-full flex-col flex-1">


        
        <div class="flex flex-col w-full gap-2 mt-20">
            <span v-if="searchError" class="text-error m-auto">Тест</span>
            <UInput placeholder="Поиск..." class="m-auto w-120" />
        </div>

        

        <div class="flex flex-row pt-20 p-10 pb-0 gap-4">
            <div class="flex flex-col h-screen w-[30%] ring ring-default shadow-sm">
                <div class="flex flex-col w-full mt-4">
                    <span class="text-medium self-center text-[1.3rem]">Фильтры</span>
                    <USeparator orientation="horizontal" class="self-center w-[80%] h-3"/>
                    <span class="text-medium self-center mt-4 mb-4">Метод</span>
                    <div class="flex flex-row gap-2 w-full justify-center content-center flex-wrap">
                        <UButton 
                                variant="outline" 
                                color="success"
                                size="sm"
                                class="flex"
                            >
                                NER
                        </UButton>
                    </div>
                    <span class="text-medium self-center mt-4 mb-4">Библиотеки</span>
                    <div class="flex flex-row gap-2 w-full justify-center content-center flex-wrap">
                        <UButton 
                            variant="outline" 
                            color="success"
                            size="sm"
                            class="flex"
                        >
                            <SiTensorflow />
                            TensorFlow
                        </UButton>
                        <UButton 
                            variant="outline" 
                            color="success"
                            size="sm"
                            class="flex"
                        >
                            <SiPytorch />
                            PyTorch
                        </UButton>
                    </div>
                    <span class="text-medium self-center mt-4 mb-4">Локализация</span>
                    <div class="flex flex-row gap-2 w-full justify-center content-center flex-wrap">
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            English
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Spanish
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Greek
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Russian
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Italian
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Chinese
                        </UButton>
                        <UButton 
                            variant="subtle" 
                            color="info"
                            size="sm"
                            class="flex"
                        >
                            Japanese
                        </UButton>
                    </div>
                </div>
            </div>

            

            <div class="flex flex-col items-center gap-5 p-3 w-full m-auto ring ring-default shadow-sm" >
                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row p-1 self-center rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="flex font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row p-1 self-center rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">English</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiTensorflow class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    Tensorflow
                                </span>
                            </div>
                            <div class="flex flex-row p-1 self-center rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Spanish</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Greek</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Russian</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Italian</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Chinese</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

                <div class="flex flex-col rounded-lg gap-4 ring ring-default shadow-sm p-4 h-50 w-full">
                    <div class="flex flex-row">
                        <div class="flex flex-row gap-4">
                            <span class="flex self-center">SomeDataset name</span>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">NER</span>
                            </div>
                            <div class="flex flex-row self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <SiPytorch class="h-4 self-center" />
                                <span class="font-bold self-center text-xs">
                                    PyTorch
                                </span>
                            </div>
                            <div class="flex flex-row  self-center p-1 rounded-lg ring ring-primary/50 shadow-sm">
                                <span class="font-bold self-center text-xs">Japanese</span>
                            </div>
                        </div>
                        <span class="flex ml-auto">Someone</span>
                    </div>
                    <USkeleton class="flex h-full w-full" />
                </div>

            </div>
        </div>
    </div>
</template>