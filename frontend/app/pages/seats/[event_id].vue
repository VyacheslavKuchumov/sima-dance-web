<template>
  <div class="w-full space-y-6">
    <header class="space-y-2">
      <p class="text-sm uppercase tracking-[0.2em] text-gray-500">Бронирование</p>
      <h1 class="text-3xl font-semibold">
        {{ event?.title || 'Выбор мест' }}
      </h1>
      <p class="text-sm text-gray-500">
        {{ eventDateLabel }}
      </p>
    </header>

    <div class="layout-grid">
      <SeatsList
        :event-id="eventId"
        :refresh-nonce="refreshNonce"
        @changed="handleBookingChange"
      />

      <BookingCart
        :event-id="eventId"
        @changed="handleBookingChange"
      />
    </div>
  </div>
</template>

<script setup>
const route = useRoute()

const eventId = computed(() => String(route.params.event_id))
const refreshNonce = ref(0)

const { data } = useFetch(() => `/api/backend/booking/events/${eventId.value}/`, {
  server: false,
  default: () => null,
})

const event = computed(() => data.value)
const eventDateLabel = computed(() => {
  if (!event.value?.starts_at) {
    return 'Выберите места слева и завершите подтверждение через корзину.'
  }

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
  }).format(new Date(event.value.starts_at))
})

function handleBookingChange() {
  refreshNonce.value += 1
}
</script>

<style scoped>
.layout-grid {
  display: grid;
  gap: 1.5rem;
}

@media (min-width: 1024px) {
  .layout-grid {
    grid-template-columns: minmax(0, 2fr) minmax(320px, 1fr);
    align-items: start;
  }
}
</style>
