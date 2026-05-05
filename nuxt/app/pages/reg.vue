<script setup lang="ts">
import { ref, onMounted, onUnmounted, h } from 'vue'
import { toTypedSchema } from '@vee-validate/zod'
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate'
import { z } from 'zod'

definePageMeta({
    layout: {
        name: 'main',
    }
})

const formSchema = z.object({
  login: z
    .string()
    .min(5, 'Длина логина не может быть меньше 5')
    .max(50, 'Длина логина не может превышать 50'),
  password: z
    .string()
    .min(8, 'Длина пароля не может быть меньше 8')
    .max(50, 'Длина пароля не может превышать 50'),
  confirmPassword: z
    .string()
  }).refine((data) => data.password === data.confirmPassword, {
  message: 'Пароли не совпадают',
  path: ['confirmPassword'] // указывает на конкретное поле ошибки
})

const { handleSubmit, errors } = useForm({
  validationSchema: toTypedSchema(formSchema),
  initialValues: {
    login: '',
    password: '',
    confirmPassword: '',
  },
})

const toast = useToast();

const onSubmit = handleSubmit(async (data) => {
    const payload = {
        username: data.login,    // login → username
        password: data.password,
        rememberMe: remember.value,
    }

    try {
        const response = await $fetch.raw("http://localhost:8000/registration", {
            method: 'POST',
            body: JSON.stringify(payload),
            credentials: "include",
        })

        if (response.status == 200) {
            navigateTo('/')
        }
    } catch (err: any) {
        if (err.response.status == 409) {
            toast.add({
                title: "Ошибка регистрации",
                description: "Пользователь с таким именем уже существует!",
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
                        class="font-mono text-7xl font-bold transform transition-all duration-200 dark:text-gray-300 text-gray-800">
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
        <div class="flex flex-col p-6 rounded-[6px] w-full absoulute -mt-45 sm:-mt-10
                    bg-transparent md:w-170 lg:w-110 m-auto
                    bg-clip-border transform transition-all duration-400">
            <UFieldGroup class="flex flex-col" :schema="formSchema" eager-validation>
              <div class="flex flex-col w-full mt-2">
                <VeeField v-slot="{ field, errorMessage }" name="login">
                  <UFormField 
                  class="mb-3 md:text-[1rem] lg:text-[1rem]" 
                  label="логин" 
                  :error="errorMessage"
                  required>
                    <UInput
                        id="login"
                        v-bind="field"
                        type="text"
                        size="lg"
                        placeholder="MyLogin" 
                        class="flex rounded-[6px]"
                        autocomplete="off"
                        :aria-invalid="!!errorMessage"
                        required
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
                    <UFormField class="text-slate-300 mb-3 md:text-[1rem] lg:text-[1rem]" label="пароль" :error="errorMessage" required>
                    <div class="flex flex-row rounded-[6px]">
                        <UInput 
                          id="password"
                          v-bind="field"
                          size="lg"
                          :type="isTogglePassword ? 'password' : 'text'"
                          :placeholder="isTogglePassword ? '••••••••' : 'password'"
                          :aria-invalid="!!errorMessage"
                          class="flex font-bold font-mono w-full
                          rounded-r-none rounded-[6px]"
                          autocomplete="off"/>
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
              <VeeField v-slot="{ field, errorMessage }" name="confirmPassword">
                <div class="flex flex-col w-full mt-2">
                <UFormField class="text-slate-300 mb-3 md:text-[1rem] lg:text-[1rem]" label="повтор пароля" :error="errorMessage" required>
                    <div class="flex flex-row rounded-[6px]">
                    <UInput 
                        id="confirmPassword"
                        v-bind="field"
                        size="lg"
                        :type="isTogglePassword ? 'password' : 'text'"
                        :placeholder="isTogglePassword ? '••••••••' : 'password'"
                        :aria-invalid="!!errorMessage"
                        class="flex font-bold font-mono w-full
                        rounded-r-none rounded-[6px]"
                        autocomplete="off"/>
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
            </div>
            <UButton
                color="primary"
                variant="outline"
                type="submit"
                class="mt-10 h-10 justify-center rounded-[8px]" 
                label="Зарегестрироваться">
            </UButton>
        </div>
    </form>
</template>