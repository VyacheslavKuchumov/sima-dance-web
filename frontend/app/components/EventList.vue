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
        <div class="flex flex-col gap-2 sm:flex-row">
          <UButton color="primary" block @click="() => showEventSeats(event.id)">
            {{ auth.isSuperuser ? 'Открыть схему' : 'Бронировать места' }}
          </UButton>

          <UButton
            v-if="auth.isSuperuser"
            color="neutral"
            variant="outline"
            block
            @click="() => editEvent(event.id)"
          >
            Редактировать
          </UButton>
        </div>
      </template>
    </UCard>
  </UContainer>
</template>

<script setup>
const auth = useAuthStore()
const router = useRouter()
const formatDate = useDateConverter()
const toast = useAppToast()

const { data, pending, error } = useFetch('/api/backend/booking/events/', {
  server: false,
  default: () => [],
})

const events = computed(() => {
  if (Array.isArray(data.value)) return data.value
  return data.value?.results ?? []
})

watch(error, (value) => {
  if (!value) return

  toast.add({
    title: 'Ошибка',
    description: value.message ?? 'Не удалось загрузить события.',
    color: 'error',
  })
})

function showEventSeats(eventId) {
  router.push(`/seats/${eventId}`)
}

function editEvent(eventId) {
  router.push({
    path: '/admin/events',
    query: {
      edit: String(eventId),
    },
  })
}
</script>
