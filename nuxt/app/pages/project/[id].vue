<script setup lang="ts">
definePageMeta({
  middleware: 'auth'
})

onMounted(() => {
  // const response = await fetch("http://localhost:8000/me");
})

import type { DropdownMenuItem, NavigationMenuItem } from '@nuxt/ui'

const auth = useAuthStore();
const open = ref(true)

const colorMode = useColorMode()

console.log()

const teams = ref([
  {
    label: 'Nuxt',
    avatar: {
      src: 'https://github.com/nuxt.png',
      alt: 'Nuxt'
    }
  },
  {
    label: 'Vue',
    avatar: {
      src: 'https://github.com/vuejs.png',
      alt: 'Vue'
    }
  },
  {
    label: 'UnJS',
    avatar: {
      src: 'https://github.com/unjs.png',
      alt: 'UnJS'
    }
  }
])
const selectedTeam = ref(teams.value[0])

const teamsItems = computed<DropdownMenuItem[][]>(() => {
  return [
    teams.value.map((team, index) => ({
      ...team,
      kbds: ['meta', String(index + 1)],
      onSelect() {
        selectedTeam.value = team
      }
    })),
    [
      {
        label: 'Create team',
        icon: 'i-lucide-circle-plus'
      }
    ]
  ]
})

function getItems(state: 'collapsed' | 'expanded') {
  return [
    {
      label: 'Изменить проект',
      icon: 'i-lucide-pencil',
    },
    {
      label: 'Добавить датасет',
      icon: 'i-lucide-list-plus'
    },
    {
      label: 'Добавить модель',
      icon: 'i-lucide-astroid'
    },
    {
      label: 'Статистика',
      icon: 'i-lucide-chart-column',
      children:
        state === 'expanded'
          ? [
              {
                label: 'Accuracy',
              },
              {
                label: 'Precision',
              },
              {
                label: 'Recall',
              },
              {
                label: 'F-score',
              }
            ]
          : []
    }
  ] satisfies NavigationMenuItem[]
}

const user = ref({
  name: 'Benjamin Canac',
  avatar: {
    src: 'https://github.com/benjamincanac.png',
    alt: 'Benjamin Canac'
  }
})

const userItems = computed<DropdownMenuItem[][]>(() => [
  [
    {
      label: 'Profile',
      icon: 'i-lucide-user'
    },
    {
      label: 'Billing',
      icon: 'i-lucide-credit-card'
    },
    {
      label: 'Settings',
      icon: 'i-lucide-settings',
      to: '/settings'
    }
  ],
  [
    {
      label: 'Appearance',
      icon: 'i-lucide-sun-moon',
      children: [
        {
          label: 'Light',
          icon: 'i-lucide-sun',
          type: 'checkbox',
          checked: colorMode.value === 'light',
          onUpdateChecked(checked: boolean) {
            if (checked) {
              colorMode.preference = 'light'
            }
          },
          onSelect(e: Event) {
            e.preventDefault()
          }
        },
        {
          label: 'Dark',
          icon: 'i-lucide-moon',
          type: 'checkbox',
          checked: colorMode.value === 'dark',
          onUpdateChecked(checked: boolean) {
            if (checked) {
              colorMode.preference = 'dark'
            }
          },
          onSelect(e: Event) {
            e.preventDefault()
          }
        }
      ]
    }
  ],
  [
    {
      label: 'GitHub',
      icon: 'i-simple-icons-github',
      to: 'https://github.com/nuxt/ui',
      target: '_blank'
    },
    {
      label: 'Log out',
      icon: 'i-lucide-log-out'
    }
  ]
])

defineShortcuts(extractShortcuts(teamsItems.value))

</script>

<template>
  <div class="flex flex-1">
    <USidebar
      v-model:open="open"
      collapsible="icon"
      rail
      :ui="{
          gap: 'h-[calc(100%-var(--ui-header-height))]',
          container:
            'absolute top-(--ui-header-height) bottom-0 h-[calc(100%-var(--ui-header-height))]'
        }"
    >
        <template #default="{ state }">
            <UNavigationMenu
                :key="state"
                :items="getItems(state)"
                orientation="vertical"
                :ui="{ link: 'p-1.5 overflow-hidden' }"
            />
        </template>

        <template #footer>
            <UButton
                icon="i-lucide-panel-left"
                color="neutral"
                variant="ghost"
                aria-label="Toggle sidebar"
                @click="open = !open"
            />
        </template>
    </USidebar>
    <div class="flex flex-col lg:w-[75%] sm:w-[65%] h-screen gap-6 p-8 transform transition-all duration-200 max-h-screen">
        <div>
            <span class="text-default font-medium">Some name for project idk</span>
        </div>

        <USkeleton class='w-full h-50 shrink-0'/>
        <USkeleton class='w-full h-20 shrink-0'/>
        <USkeleton class='w-full h-70 shrink-0'/>
        <USkeleton class='w-full h-30 shrink-0'/>

    </div>
    
    <USeparator orientation="vertical" class="h-screen" />
    
    <div class="flex flex-col lg:w-[25%] sm:w-[35%] gap-3 p-4 max-h-screen overflow-y-auto transform transition-all duration-200">
        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>
        
        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>

        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>

        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>

        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>
        
        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>

        <USkeleton class="h-[1.2rem] w-[40%] shrink-0" />
        <USkeleton class="h-60 w-full shrink-0"/>
    </div>
</div>
</template>