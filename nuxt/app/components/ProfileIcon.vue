<script setup lang="ts">
import type { DropdownMenuItem } from '@nuxt/ui'
const route = useRoute()

const auth = useAuthStore();
await auth.fetchUser();


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
    <div v-if="route.path !== '/profile'" class="m-1 flex gap-2">
        <!-- <div class="mx-auto text-center text-xs">пользователь</div> -->
        <p class="h-full self-center">{{ auth.user.login }}</p>
        <UDropdownMenu :items="items">
            <UButton icon='i-lucide-user' size="md" color="neutral" variant="outline" />
        </UDropdownMenu>
    </div>
</template>
<!-- 
профиль
сменить пользователя 
-->