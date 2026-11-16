<template>
  <UModal>
    <template #default>
      <slot name="trigger" />
    </template>
    <template #content>
      <slot />
    </template>
  </UModal>
</template>
