<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
const route = useRoute()

const auth = useAuthStore();
await auth.fetchUser();
const hideIconPages = ['/auth', '/reg', '/profile'];

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
        label: 'Выйти',
        icon: 'i-lucide-log-out',
        color: 'error',
        type: "link",
        to: "/auth"
    }
  ]
])
</script>

<template>
    <div v-if="!hideIconPages.includes(route.path)" class="m-1 flex gap-2">
        <p class="h-full self-center">{{ auth.user.login ? auth.user.login : 'Пусто' }}</p>
        <UDropdownMenu :items="items">
            <UButton icon='i-lucide-user' size="md" color="neutral" variant="outline" />
        </UDropdownMenu>
    </div>
</template>