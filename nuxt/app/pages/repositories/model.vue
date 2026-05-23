<script setup lang="ts">

import { ref, onMounted, onUnmounted, h } from 'vue'
import { toTypedSchema } from '@vee-validate/zod'
import { Form, ErrorMessage, useForm, Field as VeeField } from 'vee-validate'
import { toast } from 'vue-sonner'
import type { collapsible } from '#build/ui'
import type { TreeItem } from '@nuxt/ui'

definePageMeta({
  middleware: 'auth',
  layout: {
    name: 'main'
  }
})

const items = ref<TreeItem[]>([
  {
    label: 'app/',
    defaultExpanded: true,
    children: [
      {
        label: 'composables/',
        children: [
          {
            label: 'useAuth.ts',
            icon: 'i-vscode-icons-file-type-typescript'
          },
          {
            label: 'useUser.ts',
            icon: 'i-vscode-icons-file-type-typescript'
          }
        ]
      },
      {
        label: 'components/',
        defaultExpanded: true,
        children: [
          {
            label: 'Card.vue',
            icon: 'i-vscode-icons-file-type-vue'
          },
          {
            label: 'Button.vue',
            icon: 'i-vscode-icons-file-type-vue'
          }
        ]
      }
    ]
  },
  {
    label: 'app.vue',
    icon: 'i-vscode-icons-file-type-vue'
  },
  {
    label: 'nuxt.config.ts',
    icon: 'i-vscode-icons-file-type-nuxt'
  }
])
</script>

<template>
  <div class="flex container">
    <h1 class="font-mono text-2xl">
      /public
    </h1>
  </div>
  <div class="flex container">
    <UTree :items="items" />
  </div>
</template>
