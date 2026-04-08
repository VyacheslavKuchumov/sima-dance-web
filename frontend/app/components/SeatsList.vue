<template>
  <UCard class="w-full">
    <template #header>
      <div class="space-y-3">
        <div class="flex items-center justify-between gap-3">
          <div>
            <h2 class="text-xl font-semibold">План зала</h2>
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
          <template v-if="isAdminMode">
            <div class="legend-item"><span class="legend-dot seat-available-admin" /> Свободно</div>
            <div class="legend-item"><span class="legend-dot seat-held-admin" /> Удерживается</div>
            <div class="legend-item"><span class="legend-dot seat-booked-admin" /> Подтверждено</div>
            <div class="legend-item"><span class="legend-dot seat-unavailable" /> Отключено</div>
          </template>

          <template v-else>
            <div class="legend-item"><span class="legend-dot seat-available-user" /> Свободно</div>
            <div class="legend-item"><span class="legend-dot seat-held-current" /> В вашей корзине</div>
            <div class="legend-item"><span class="legend-dot seat-booked-current" /> Уже подтверждено</div>
            <div class="legend-item"><span class="legend-dot seat-booked" /> Забронировано</div>
          </template>
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
                    'seat-available-admin': isAdminMode && seatStatus(seat) === 'available',
                    'seat-available-user': !isAdminMode && seatStatus(seat) === 'available',
                    'seat-held': !isAdminMode && seatStatus(seat) === 'held',
                    'seat-held-current': !isAdminMode && seatStatus(seat) === 'held-current',
                    'seat-booked': !isAdminMode && seatStatus(seat) === 'booked',
                    'seat-booked-current': !isAdminMode && seatStatus(seat) === 'booked-current',
                    'seat-held-admin': isAdminMode && ['held', 'held-current'].includes(seatStatus(seat)),
                    'seat-booked-admin': isAdminMode && ['booked', 'booked-current'].includes(seatStatus(seat)),
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
      <p class="text-sm text-muted">
        {{
          isAdminMode
            ? 'Нажмите на любое место, чтобы открыть расширенное управление бронью. Удаление самого места в этом окне недоступно.'
            : 'Нажмите на свободное место, чтобы удержать его. Повторный клик по месту в вашей корзине снимает удержание.'
        }}
      </p>
    </template>
  </UCard>

  <AdminSeatDialog
    v-if="selectedSeat"
    v-model:open="adminDialogOpen"
    :event-id="eventId"
    :seat="selectedSeat"
    @changed="handleAdminSeatChanged"
  />
</template>

<script setup>
const props = defineProps({
  eventId: {
    type: [String, Number],
    required: true,
  },
})

const emit = defineEmits(['admin-changed'])

const auth = useAuthStore()
const bookingStore = useBookingStore()
const toast = useAppToast()

const currentUserId = computed(() => auth.userId ?? auth.user?.id ?? null)
const isAdminMode = computed(() => auth.isSuperuser)
const eventId = computed(() => String(props.eventId))
const activeSeatId = ref(null)
const isRefreshing = ref(false)
const refreshQueuePending = ref(false)
const adminDialogOpen = ref(false)
const selectedSeat = ref(null)

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
  if (isAdminMode.value) return []
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
  if (isAdminMode.value) {
    selectedSeat.value = seat
    adminDialogOpen.value = true
    return
  }

  const status = seatStatus(seat)
  activeSeatId.value = seat.id

  try {
    if (status === 'available') {
      await bookingStore.holdSeat({ eventId: eventId.value, seatId: seat.id })

      toast.add({
        title: 'Место удержано',
        description: 'Место добавлено. Откройте корзину, чтобы подтвердить бронь.',
        color: 'success',
        actions: [{
          label: 'Перейти в корзину',
          color: 'neutral',
          variant: 'outline',
          to: '/cart',
        }],
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

    if (status === 'booked') {
      toast.add({
        title: 'Место забронировано',
        description: 'Оно уже подтверждено другим пользователем.',
        color: 'warning',
      })
      return
    }

    if (status === 'held') {
      toast.add({
        title: 'Место временно занято',
        description: 'Сейчас оно находится в корзине другого пользователя.',
        color: 'warning',
      })
      return
    }

    toast.add({
      title: 'Место недоступно',
      description: 'Оно сейчас недоступно для бронирования.',
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

async function handleAdminSeatChanged() {
  await refreshSeatMap({ syncCart: false })
  emit('admin-changed')
}

const { connectionState } = useSeatmapRealtimeSync({
  eventId,
  onMessage: () => {
    void refreshSeatMap({ syncCart: !isAdminMode.value })
      .then(() => {
        if (isAdminMode.value) {
          emit('admin-changed')
        }
      })
      .catch((error) => {
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
  void refreshSeatMap({ syncCart: !isAdminMode.value }).catch((error) => {
    console.error('Failed to refresh seatmap after event change', error)
  })
})

onMounted(async () => {
  if (isAdminMode.value) return

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

watch(adminDialogOpen, (value) => {
  if (!value) {
    selectedSeat.value = null
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

.seat-available-admin {
  background: #e6ffed;
  border-color: #49a36b;
  color: #0b4d28;
}

.seat-available-user {
  background: #dbeafe;
  border-color: #2563eb;
  color: #1e3a8a;
}

.seat-held {
  background: #f3f3f4;
  color: #8a8a8a;
  cursor: not-allowed;
}

.seat-held-current {
  background: #ffedd5;
  border-color: #f97316;
  color: #9a3412;
}

.seat-held-admin {
  background: #ffedd5;
  border-color: #f97316;
  color: #9a3412;
}

.seat-unavailable {
  background: #f3f3f4;
  color: #8a8a8a;
  cursor: not-allowed;
}

.seat-booked {
  background: #dcfce7;
  border-color: #16a34a;
  color: #166534;
  cursor: not-allowed;
}

.seat-booked-current {
  background: #dcfce7;
  border-color: #16a34a;
  color: #166534;
}

.seat-booked-admin {
  background: #fee2e2;
  border-color: #dc2626;
  color: #991b1b;
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
