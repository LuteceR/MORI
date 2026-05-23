<script setup lang="ts">
definePageMeta({
    layout: {
        name: 'main',
    }
})

const auth = useAuthStore();

import { ref, onMounted, onUnmounted, h } from 'vue';
import { toTypedSchema } from '@vee-validate/zod';
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate';
import { z } from 'zod';

const formSchema = z.object({
  login: z
    .string()
    .min(5, 'Длина пароля не может быть меньше 5')
    .max(50, 'Длина пароля не может превышать 50'),
  password: z
    .string()
    .min(8, 'Пароль короче 8 символов')
    .max(50, 'Пароль длиннее 50 символов'),
})

const { handleSubmit, errors } = useForm({
  validationSchema: toTypedSchema(formSchema),
  initialValues: {
    login: '',
    password: '',
  },
})

const toast = useToast();

const onSubmit = handleSubmit(async (data) => {
    const payload = {
        username: data.login,
        password: data.password,
        rememberMe: remember.value,
    }
  
    try {
        const response = await $fetch.raw("http://localhost:8000/authorization", {
            method: 'POST',
            body: JSON.stringify(payload),
            credentials: "include",
        })

        if (response.status == 200) {
            auth.setUser({
                "name": payload.username
            })
            navigateTo('/')
        }
    } catch (err: any) {
        if (err.response.status == 401) {
            toast.add({
                title: "Ошибка входа",
                description: "Неправильный логин или пароль",
                icon: 'i-lucide-log-in',
            })
        }
    }
})

const isTogglePassword = ref(true);
const remember = ref(false);

</script>

<template>
        <div>
            <div class="mx-auto sm:mt-25 mt-5 px-4 py-20">
                <div class="flex flex-col items-center text-center space-y-4">
                    <div id="logo" class="flex items-center flex-col">
                        <h1 
                        class="font-mono text-7xl font-bold dark:text-gray-300 text-gray-800 transform transition-all duration-200">
                            МОРИ
                        </h1>
                        <p 
                        class="mt-4 font-sans text-2xl/2 opacity-0 sm:opacity-100 dark:text-gray-300 text-gray-800
                                transform transition-all duration-200">
                            Машинное Обучение :
                        </p>
                        <p class="mt-2 font-sans text-2xl opacity-0 sm:opacity-100 dark:text-gray-300 text-gray-800
                                transform transition-all duration-200">
                            Разворачивание и Исследование
                        </p>
                    </div>
                </div>
            </div>
        </div>

    <form id="authForm" @submit="onSubmit">
        <div class="flex flex-col p-6 rounded-md w-full absoulute -mt-45 sm:-mt-10
                    bg-transparent md:w-170 lg:w-110 m-auto
                    transform transition-all duration-400">
            <UFieldGroup class="flex flex-col" :schema="formSchema" eager-validation>
              <div class="flex flex-col w-full mt-2">
                <VeeField v-slot="{ field, errorMessage }" name="login">
                  <UFormField class="mb-3 md:text-[1rem] lg:text-[1rem]" label="логин" :error="errorMessage">
                    <UInput
                        id="login"
                        v-bind="field"
                        type="login"
                        size="lg"
                        placeholder="MyLogin"
                        class="w-full"
                        :aria-invalid="errorMessage? true : false"
                        :ui="{
                            base: [
                                'rounded-md!'
                            ]
                        }"
                        />
                  </UFormField>
                </VeeField>
              </div>
              <VeeField v-slot="{ field, errorMessage }" name="password">
                <div class="flex flex-col w-full mt-2">
                    <UFormField class="text-slate-300 mb-3 md:text-[1rem] lg:text-[1rem]" label="пароль" :error="errorMessage">
                    <div class="flex flex-row rounded-md">
                        <UInput 
                          id="password"
                          v-bind="field"
                          size="lg"
                          :type="isTogglePassword ? 'password' : 'text'"
                          :placeholder="isTogglePassword ? '••••••••' : 'password'"
                          :aria-invalid="!!errorMessage"
                          class="flex w-full h-full font-bold font-mono transform 
                          transition-all duration-400 mr-auto"/>
                    <UButton 
                        @click = 'isTogglePassword = !isTogglePassword' 
                        variant="outline" 
                        size="lg"
                        class="flex self-center rounded-l-none"
                        :icon="isTogglePassword ? 'i-lucide-eye' : 'i-lucide-eye-off'"
                        :color='errorMessage? "error" : "primary"'>
                    </UButton>
                    </div>
                    </UFormField>
                </div>
              </VeeField>
            </UFieldGroup>
            <div class="flex flex-row justify-between w-full mt-4 space-x-4">
                <div class="flex gap-2">
                    <USwitch
                    v-model="remember" 
                    id="rememberMe" 
                    class=""/>
                    <UFormField label="Запомнить меня"></UFormField>
                </div>
                <ULink as="button" href="/reg" right>не зарегестрированы?</ULink>
            </div>
            <UButton
                color="primary"
                variant="outline"
                type="submit"
                class="mt-10 justify-center h-10 rounded-[8px]" 
                label="Войти">
            </UButton>
        </div>
    </form>
</template>