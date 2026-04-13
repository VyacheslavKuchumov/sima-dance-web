<template>
  <UContainer class="w-full max-w-5xl py-8">
    <div class="space-y-4">
      <div class="space-y-2">
        <h1 class="text-3xl font-semibold">Мои брони</h1>
        <p class="text-sm text-muted">
          Здесь собраны ваши активные удержания и уже подтвержденные места по всем событиям.
        </p>
      </div>

      <BookingCart title="Все мои брони" @changed="reload" />
    </div>
  </UContainer>
</template>

<script setup>
const booking = useBookingStore()

async function reload() {
  await booking.fetchBookings({
    statuses: ['held', 'booked'],
    activeOnly: true,
  })
}

onMounted(() => {
  void reload()
})
</script>
