<template>
  <div class="w-full max-w-6xl py-8">
    <AdminEventsManager />
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'superuser',
})
</script>
