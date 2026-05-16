<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
const route = useRoute()
const items = ref<DropdownMenuItem[][]>([
  [
    {
        label: 'Профиль',
        icon: 'i-lucide-user',
        color: 'secondary',
        // onSelect: (e) => {},
        type: "link",
        to: "/profile"
    },
    {
        label: 'Сменить аккаунт',
        icon: 'i-lucide-log-out',
        color: 'error',
        type: "link",
        to: "/auth"
    }
  ]
])
</script>

<template>
    <div v-if="route.path !== '/profile'" class="m-1 flex gap-2">
        <svg class="w-10 m-auto" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24">
            <path fill="currentColor" d="M12 4a4 4 0 1 1 0 8a4 4 0 0 1 0-8m0 16s8 0 8-2c0-2.4-3.9-5-8-5s-8 2.6-8 5c0 2 8 2 8 2" />
        </svg>
        <!-- <div class="mx-auto text-center text-xs">пользователь</div> -->
        <UDropdownMenu :items="items">
            <UButton icon="i-lucide-menu" color="neutral" variant="outline" />
        </UDropdownMenu>
    </div>
</template>
<!-- 
профиль
сменить пользователя 
-->