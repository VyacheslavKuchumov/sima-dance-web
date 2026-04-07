<script setup>
definePageMeta({
  middleware: 'superuser',
})

await navigateTo('/admin/users')
</script>
