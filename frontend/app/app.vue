<!-- app.vue -->
<template>
  <UApp :toaster="toaster">
    <div class="app-shell">
      <NavBar />
      <UContainer class="app-content flex w-full min-w-0 items-center justify-center">
        <NuxtPage class="mt-15 w-full min-w-0" />
      </UContainer>
    </div>
  </UApp>
</template>

<script setup lang="ts">
const toaster = {
  position: 'bottom-right' as const,
  ui: {
    viewport: [
      'app-safe-toast-offset',
      'left-4',
      'right-4',
      'w-auto',
      'sm:left-auto',
      'sm:w-96',
    ].join(' '),
  },
}
</script>
