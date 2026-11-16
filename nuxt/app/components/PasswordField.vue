<script setup lang="ts">
const props = defineProps<{
  error?: boolean
}>()

const visible = defineModel<boolean>('visible', { default: false })

defineSlots<{
  default(props: { type: 'password' | 'text', placeholder: string }): unknown
}>()
</script>

<template>
  <div class="flex flex-row rounded-md">
    <slot
      :type="visible ? 'text' : 'password'"
      :placeholder="visible ? 'password' : '••••••••'"
    />
    <UButton
      type="button"
      variant="outline"
      size="lg"
      class="flex self-center rounded-l-none"
      :icon="visible ? 'i-lucide-eye-off' : 'i-lucide-eye'"
      :color="props.error ? 'error' : 'primary'"
      @click="visible = !visible"
    />
  </div>
</template>
