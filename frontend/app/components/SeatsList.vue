<template>
  <UCard class="w-full min-w-0 overflow-hidden">
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
            <div class="legend-item"><span class="legend-dot seat-held-current" /> Ожидает подтверждения</div>
            <div class="legend-item"><span class="legend-dot seat-booked-current" /> Забронировано</div>
            <div class="legend-item"><span class="legend-dot seat-booked" /> Занято другим пользователем</div>
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
            : 'Нажмите на свободное место, чтобы удержать его. Повторный клик по месту в ваших бронях снимает удержание.'
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
const STATUS_TOAST_ID = 'seat-booking-status'

const auth = useAuthStore()
const bookingStore = useBookingStore()
const toast = useAppToast()

const currentUserId = computed(() => auth.userId ?? auth.user?.id ?? null)
const isAdminMode = computed(() => auth.isSuperuser)
const eventId = computed(() => String(props.eventId))
const activeSeatId = ref(null)
const adminDialogOpen = ref(false)
const selectedSeat = ref(null)

const { data, pending, error, refresh } = useFetch(
  () => `/api/backend/booking/events/${eventId.value}/seatmap/`,
  {
    server: false,
    default: () => [],
  }
)

const seats = computed(() => Array.isArray(data.value) ? data.value : [])
const heldBookings = computed(() => bookingStore.heldBookingsForEvent(eventId.value))
const bookedBookings = computed(() => bookingStore.bookedBookingsForEvent(eventId.value))
const heldBookingsBySeat = computed(() => bookingStore.heldBookingMapForEvent(eventId.value))

watch(error, (value) => {
  if (!value) return

  toast.add({
    title: 'Не удалось загрузить схему',
    description: value.message ?? 'Попробуйте обновить страницу.',
    color: 'error',
  })
})

function replaceSeats(nextSeats) {
  data.value = Array.isArray(nextSeats) ? nextSeats : []
}

function findSeatIndex(seatId) {
  return seats.value.findIndex((item) => Number(item.id) === Number(seatId))
}

function findSeatById(seatId) {
  const index = findSeatIndex(seatId)
  return index === -1 ? null : seats.value[index]
}

function buildSeatState({ existingSeat = {}, seat, booking, action } = {}) {
  const seatAvailable = Boolean(seat?.available ?? existingSeat.available)
  const bookingStatus =
    action !== 'deleted' && booking?.status === 'booked'
      ? 'booked'
      : action !== 'deleted' && booking?.status === 'held'
        ? 'held'
        : seatAvailable
          ? 'available'
          : 'unavailable'

  const isActiveBooking = bookingStatus === 'held' || bookingStatus === 'booked'

  return {
    ...existingSeat,
    ...(seat ?? {}),
    available: seatAvailable && !isActiveBooking,
    booking_status: bookingStatus,
    user_id: isActiveBooking ? booking?.user_id ?? null : null,
    held_until: bookingStatus === 'held' ? booking?.expires_at ?? null : null,
    price: seat?.price ?? existingSeat.price ?? null,
  }
}

function toSeatmapChangePayload(booking, action = 'updated') {
  if (!booking?.seat?.id) return null

  return {
    action,
    booking: {
      id: booking.id,
      event_id: booking.event,
      user_id: booking.user_id,
      status: booking.status,
      created_at: booking.created_at ?? null,
      expires_at: booking.expires_at ?? null,
      updated_at: booking.updated_at ?? null,
      price_snapshot: booking.price_snapshot ?? null,
      is_paid: booking.is_paid ?? false,
      is_ticket_issued: booking.is_ticket_issued ?? false,
    },
    seat: {
      id: booking.seat.id,
      section: booking.seat.section,
      row: booking.seat.row,
      number: booking.seat.number,
      available: booking.seat.available,
      price: booking.seat.price ?? null,
    },
  }
}

function applySeatChange(payload) {
  if (!payload?.seat?.id) return

  const index = findSeatIndex(payload.seat.id)
  if (index === -1) return

  const nextSeats = [...seats.value]
  const existingSeat = nextSeats[index]
  const nextSeat = buildSeatState({
    existingSeat,
    seat: payload.seat,
    booking: payload.booking,
    action: payload.action,
  })

  nextSeats.splice(index, 1, nextSeat)
  replaceSeats(nextSeats)

  if (selectedSeat.value && Number(selectedSeat.value.id) === Number(nextSeat.id)) {
    selectedSeat.value = nextSeat
  }
}

function syncBookingStatusToast() {
  if (isAdminMode.value) {
    toast.remove(STATUS_TOAST_ID)
    return
  }

  if (heldBookings.value.length > 0) {
    toast.add({
      id: STATUS_TOAST_ID,
      title: 'Нужно подтвердить места и оплатить билеты',
      description: 'Откройте «Мои брони», подтвердите выбранные места и перейдите к оплате билетов.',
      color: 'warning',
      duration: false,
      actions: [createBookingToastAction()],
    })
    return
  }

  if (bookedBookings.value.length > 0) {
    toast.add({
      id: STATUS_TOAST_ID,
      title: 'Не забудьте оплатить билеты',
      description: 'Если оплата еще не выполнена, откройте «Мои брони» и завершите ее.',
      color: 'success',
      duration: 5000,
      actions: [createBookingToastAction()],
    })
    return
  }

  toast.remove(STATUS_TOAST_ID)
}

function createBookingToastAction() {
  return {
    label: 'Мои брони',
    color: 'primary',
    variant: 'solid',
    size: 'lg',
    class: 'mx-auto flex min-w-48 justify-center self-center px-6',
    to: '/cart',
  }
}

async function onSeatClick(seat) {
  if (isAdminMode.value) {
    selectedSeat.value = seat
    adminDialogOpen.value = true
    return
  }

  const currentSeat = findSeatById(seat.id) ?? seat
  const status = seatStatus(currentSeat)
  activeSeatId.value = currentSeat.id

  try {
    if (status === 'available') {
      const latestSeat = findSeatById(currentSeat.id) ?? currentSeat
      const latestStatus = seatStatus(latestSeat)

      if (latestStatus !== 'available') {
        toast.add({
          title: 'Место уже обновилось',
          description: 'Проверьте актуальный статус места на схеме.',
          color: 'warning',
        })
        return
      }

      const booking = await bookingStore.holdSeat({ eventId: eventId.value, seatId: latestSeat.id })
      const payload = toSeatmapChangePayload(booking, 'updated')
      if (payload) applySeatChange(payload)
      return
    }

    if (status === 'held-current') {
      const booking = heldBookingsBySeat.value[currentSeat.id]

      if (!booking) {
        throw new Error('Не нашли удержание для выбранного места.')
      }

      const releasedBooking = await bookingStore.releaseBooking({ eventId: eventId.value, bookingId: booking.id })
      const payload = toSeatmapChangePayload(releasedBooking, 'deleted')
      if (payload) applySeatChange(payload)
      toast.add({
        title: 'Удержание снято',
        description: 'Место снова доступно для бронирования.',
        color: 'success',
      })
      return
    }

    if (status === 'booked-current') {
      toast.add({
        title: 'Место уже забронировано',
        description: 'Оно уже закреплено за вами и показано в блоке «Мои брони».',
        color: 'info',
      })
      return
    }

    if (status === 'booked' || status === 'unavailable') {
      toast.add({
        title: 'Место забронировано другим пользователем',
        description: 'Выберите другое место на схеме зала.',
        color: 'warning',
      })
      return
    }

    if (status === 'held') {
      toast.add({
        title: 'Место временно занято',
        description: 'Сейчас оно находится в бронированиях другого пользователя.',
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
  emit('admin-changed')
}

const { connectionState } = useSeatmapRealtimeSync({
  eventId,
  onMessage: (payload) => {
    applySeatChange(payload)

    if (isAdminMode.value) {
      emit('admin-changed')
      return
    }

    bookingStore.applyRealtimeBookingChange({
      eventId: eventId.value,
      action: payload.action,
      booking: payload.booking,
      seat: payload.seat,
      currentUserId: currentUserId.value,
    })
  },
})

watch(connectionState, (nextState, previousState) => {
  if (previousState !== 'reconnecting' || nextState !== 'connected') return

  void refresh().catch((refreshError) => {
    console.error('Failed to resync seatmap after websocket reconnect', refreshError)
  })
})

const {
  groupedSeats,
  sortedRowKeys,
  seatStatus,
} = useVenueSeats(seats, currentUserId)

watch(
  () => [isAdminMode.value, eventId.value, heldBookings.value.length, bookedBookings.value.length],
  () => {
    syncBookingStatusToast()
  },
  { immediate: true }
)

onMounted(async () => {
  if (isAdminMode.value) return

  try {
    await bookingStore.fetchBookings({
      eventId: eventId.value,
      statuses: ['held', 'booked'],
      activeOnly: true,
    })
  } catch (error) {
    console.error('Failed to sync bookings on mount', error)
    toast.add({
      title: 'Не удалось синхронизировать брони',
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

onBeforeUnmount(() => {
  toast.remove(STATUS_TOAST_ID)
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
  background: #bbf7d0;
  border-color: #16a34a;
  color: #14532d;
}

.seat-available-user {
  background: #bfdbfe;
  border-color: #2563eb;
  color: #1e3a8a;
}

.seat-held-current {
  background: #fed7aa;
  border-color: #ea580c;
  color: #9a3412;
}

.seat-held-admin {
  background: #fdba74;
  border-color: #ea580c;
  color: #7c2d12;
}

.seat-unavailable {
  background: #e5e7eb;
  border-color: #cbd5e1;
  color: #6b7280;
  cursor: not-allowed;
}

.seat-held,
.seat-booked {
  background: #fecaca;
  border-color: #dc2626;
  color: #991b1b;
  cursor: not-allowed;
}

.seat-booked-current {
  background: #bbf7d0;
  border-color: #16a34a;
  color: #166534;
}

.seat-booked-admin {
  background: #fca5a5;
  border-color: #dc2626;
  color: #7f1d1d;
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
