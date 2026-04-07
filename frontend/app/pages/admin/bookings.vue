<template>
  <div class="w-full max-w-6xl py-8">
    <AdminBookingsManager />
  </div>
</template>

<script setup>
definePageMeta({
  middleware: 'superuser',
})
</script>
