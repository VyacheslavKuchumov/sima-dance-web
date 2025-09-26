<template>
    <UContainer>
    <!-- show loader while fetching -->
    <UProgress v-if="pending" animation="swing" />

    <!-- events list -->
    <UCard
      v-else
      v-for="event in events"
      :key="event.id"
      class="mb-4 max-w-md mx-auto"
      :ui="{
        header: 'p-0 sm:px-0' // Remove padding from header slot
      }"
    >
      <template #header>
        <NuxtImg src="/img/event.jpg" alt="Здесь должна быть картинка..." class="object-cover" />
      </template>

      <p class="text-2xl">{{ event.title }}</p>
      <p>{{ formatDate.isoToRu(event.starts_at) }}</p>

      <template #footer>
        <UButton color="primary" block @click="() => showEventSeats(event.id)">
          Бронировать места
        </UButton>
      </template>
    </UCard>


  </UContainer>
</template>

<script setup>

const config = useRuntimeConfig()
// composables used in your original component
const formatDate = useDateConverter()
const toast = useToast()

// Fetch events with useFetch (no store)
// Adjust endpoint if your API route differs
const { data, pending, error } = useFetch(`${config.public.BACKEND_URL}/api/booking/events/`, {
  // automatic fetch on setup; remove or change options if needed
  // e.g. headers, credentials, baseURL, etc.
})

// Computed array for template safety (always an array)
const events = computed(() => {
  // If API returns { results: [...] } adapt accordingly:
  // return events.value?.results ?? []
  return data.value?.results ?? []
})

if (error.value){
  toast.add({ title: 'Ошибка', description: `Не удалось загрузить события ${error.value}`, color: 'error' })
}


// navigation to seats page
function showEventSeats(eventId) {
  const router = useRouter()
  router.push(`/seats/${eventId}`)
}
</script>
