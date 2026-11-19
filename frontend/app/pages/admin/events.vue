<template>
  <div class="w-full max-w-6xl space-y-6 py-8">
    <AdminSeatRevenue />
    <AdminEventsManager />
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'superuser',
})
</script>
