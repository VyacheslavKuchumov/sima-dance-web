<template>
  <UCard class="w-full">
    <template #header>
      <div class="space-y-3">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold">План зала</h2>
            <p class="text-sm text-gray-500">
              Карта обновляется по push-событиям, без перезагрузки страницы и без polling.
            </p>
          </div>

          <UBadge
            v-if="connectionState === 'connected'"
            color="success"
            variant="subtle"
          >
            Live
          </UBadge>

          <UBadge
            v-else-if="connectionState === 'connecting' || connectionState === 'reconnecting'"
            color="warning"
            variant="subtle"
          >
            Syncing
          </UBadge>
        </div>

        <div class="legend">
          <div class="legend-item"><span class="legend-dot seat-available" /> Свободно</div>
          <div class="legend-item"><span class="legend-dot seat-held-current" /> В вашей корзине</div>
          <div class="legend-item"><span class="legend-dot seat-booked-current" /> Уже подтверждено</div>
          <div class="legend-item"><span class="legend-dot seat-booked" /> Недоступно</div>
        </div>
      </div>
    </template>

    <UProgress v-if="pending && !seats.length" animation="swing" />

    <DraggableContainer v-else label="Схема мест" class="max-h-110 md:max-h-150">
      <div
        v-for="(rows, section) in groupedSeats"
        :key="section"
        class="section-container"
      >
        <h3 class="section-title">{{ section }}</h3>

        <div
          v-for="rowNumber in sortedRowKeys(rows)"
          :key="rowNumber"
          class="row-container"
        >
          <div class="row-label">Ряд {{ rowNumber }}</div>

          <div class="seats-row">
            <div
              v-for="(seat, idx) in rows[rowNumber]"
              :key="seat ? `s-${seat.id}` : `gap-${idx}`"
              class="seat-circle-wrapper"
            >
              <template v-if="seat">
                <button
                  type="button"
                  class="seat-circle"
                  :class="{
                    'seat-available': seatStatus(seat) === 'available',
                    'seat-held': seatStatus(seat) === 'held',
                    'seat-held-current': seatStatus(seat) === 'held-current',
                    'seat-booked': seatStatus(seat) === 'booked',
                    'seat-booked-current': seatStatus(seat) === 'booked-current',
                    'seat-unavailable': seatStatus(seat) === 'unavailable',
                    'seat-busy': activeSeatId === seat.id,
                  }"
                  :disabled="activeSeatId === seat.id"
                  @click="onSeatClick(seat)"
                >
                  <span class="seat-number">{{ seat.number }}</span>
                </button>

                <div class="seat-price" v-if="seat.price">
                  {{ parseInt(seat.price, 10) }}₽
                </div>
                <div class="seat-price seat-price-empty" v-else>
                  —
                </div>
              </template>

              <template v-else>
                <div class="seat-gap"></div>
              </template>
            </div>
          </div>
        </div>
      </div>
    </DraggableContainer>

    <template #footer>
      <p class="text-sm text-gray-500">
        Нажмите на свободное место, чтобы удержать его. Повторный клик по месту в вашей корзине снимает удержание.
      </p>
    </template>
  </UCard>
</template>

<script setup>
const props = defineProps({
  eventId: {
    type: [String, Number],
    required: true,
  },
})

const auth = useAuthStore()
const bookingStore = useBookingStore()
const toast = useAppToast()

const currentUserId = computed(() => auth.userId ?? auth.user?.id ?? null)
const eventId = computed(() => String(props.eventId))
const activeSeatId = ref(null)
const isRefreshing = ref(false)
const refreshQueuePending = ref(false)

const { data, pending, error, refresh } = useFetch(
  () => `/api/backend/booking/events/${eventId.value}/seatmap/`,
  {
    server: false,
    default: () => [],
  }
)

const seats = computed(() => data.value ?? [])
const heldBookingsBySeat = computed(() => bookingStore.heldBookingMapForEvent(eventId.value))

watch(error, (value) => {
  if (!value) return

  toast.add({
    title: 'Не удалось загрузить схему',
    description: value.message ?? 'Попробуйте обновить страницу.',
    color: 'error',
  })
})

async function syncBookings() {
  await bookingStore.fetchEventBookings({ eventId: eventId.value, force: true })
}

async function refreshSeatMap({ syncCart = false } = {}) {
  if (isRefreshing.value) {
    refreshQueuePending.value = true
    return
  }

  isRefreshing.value = true

  try {
    const tasks = [refresh()]
    if (syncCart) {
      tasks.push(syncBookings())
    }
    await Promise.all(tasks)
  } finally {
    isRefreshing.value = false

    if (refreshQueuePending.value) {
      refreshQueuePending.value = false
      await refreshSeatMap({ syncCart: true })
    }
  }
}

async function onSeatClick(seat) {
  const status = seatStatus(seat)
  activeSeatId.value = seat.id

  try {
    if (status === 'available') {
      await bookingStore.holdSeat({ eventId: eventId.value, seatId: seat.id })
      const isMobileLayout = import.meta.client && window.innerWidth < 1024

      toast.add({
        title: 'Место удержано',
        description: isMobileLayout
          ? 'Место добавлено. Откройте корзину, чтобы подтвердить бронь.'
          : 'Оно добавлено в корзину справа.',
        color: 'success',
        actions: isMobileLayout
          ? [{
              label: 'Перейти в корзину',
              color: 'neutral',
              variant: 'outline',
              to: '/cart',
            }]
          : [],
      })
      toast.add({
        title: 'Подтвердите бронь',
        description: 'Место удерживается 30 минут. Завершите подтверждение в корзине, чтобы закрепить его за собой.',
        color: 'warning',
      })
      await refreshSeatMap({ syncCart: true })
      return
    }

    if (status === 'held-current') {
      let booking = heldBookingsBySeat.value[seat.id]

      if (!booking) {
        await syncBookings()
        booking = heldBookingsBySeat.value[seat.id]
      }

      if (!booking) {
        throw new Error('Не нашли удержание для выбранного места.')
      }

      await bookingStore.releaseBooking({ eventId: eventId.value, bookingId: booking.id })
      toast.add({
        title: 'Удержание снято',
        description: 'Место снова доступно для бронирования.',
        color: 'success',
      })
      await refreshSeatMap({ syncCart: true })
      return
    }

    if (status === 'booked-current') {
      toast.add({
        title: 'Место уже подтверждено',
        description: 'Оно уже закреплено за вами и показано в нижнем блоке корзины.',
        color: 'info',
      })
      return
    }

    toast.add({
      title: 'Место недоступно',
      description: 'Оно уже занято или удерживается другим пользователем.',
      color: 'warning',
    })
  } catch (err) {
    toast.add({
      title: 'Не удалось изменить бронь',
      description: err?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  } finally {
    activeSeatId.value = null
  }
}

const { connectionState } = useSeatmapRealtimeSync({
  eventId,
  onMessage: () => {
    void refreshSeatMap({ syncCart: true }).catch((error) => {
      console.error('Failed to refresh seatmap after websocket update', error)
    })
  },
})

const {
  groupedSeats,
  sortedRowKeys,
  seatStatus,
} = useVenueSeats(seats, currentUserId)

watch(eventId, () => {
  void refreshSeatMap({ syncCart: true }).catch((error) => {
    console.error('Failed to refresh seatmap after event change', error)
  })
})

onMounted(async () => {
  try {
    await syncBookings()
  } catch (error) {
    console.error('Failed to sync bookings on mount', error)
  toast.add({
    title: 'Не удалось синхронизировать корзину',
    description: 'Схема зала останется доступной, попробуйте обновить позже.',
    color: 'warning',
  })
  }
})
</script>

<style scoped>
.section-container {
  margin-bottom: 1.75rem;
  padding-bottom: 0.75rem;
}

.section-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.05rem;
}

.row-container {
  display: flex;
  align-items: center;
  margin: 0.35rem 0;
}

.row-label {
  width: 56px;
  text-align: right;
  margin-right: 12px;
  font-weight: 600;
}

.seats-row {
  display: flex;
  gap: 10px;
  flex-wrap: nowrap;
  align-items: center;
}

.seat-circle-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 48px;
}

.seat-gap {
  width: 48px;
  height: 48px;
}

.seat-circle {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  border: 2px solid transparent;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  user-select: none;
  transition: transform 0.15s ease, opacity 0.15s ease;
}

.seat-circle:not(:disabled):hover {
  transform: translateY(-1px);
}

.seat-number {
  font-size: 0.95rem;
  font-weight: 600;
}

.seat-price {
  margin-top: 6px;
  font-size: 0.75rem;
  text-align: center;
}

.seat-available {
  background: #e6ffed;
  border-color: #49a36b;
  color: #0b4d28;
}

.seat-held {
  background: #f3f3f4;
  color: #8a8a8a;
  cursor: not-allowed;
}

.seat-held-current {
  background: #dbeafe;
  border-color: #2563eb;
  color: #1e3a8a;
}

.seat-unavailable {
  background: #f3f3f4;
  color: #8a8a8a;
  cursor: not-allowed;
}

.seat-booked {
  background: #f3f3f4;
  color: #8a8a8a;
  cursor: not-allowed;
}

.seat-booked-current {
  background: #fff1c6;
  border-color: #d49e2d;
  color: #5a3d00;
}

.seat-busy {
  opacity: 0.55;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem 1rem;
  font-size: 0.9rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-dot {
  width: 14px;
  height: 14px;
  border-radius: 999px;
  border: 1px solid transparent;
}
</style>
