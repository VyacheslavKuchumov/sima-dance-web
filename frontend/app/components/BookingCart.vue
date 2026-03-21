<template>
  <UCard class="w-full">
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold">{{ title }}</h2>
          <p class="text-sm text-gray-500">
            Удержанные места хранятся на сервере и восстановятся после обновления страницы.
          </p>
        </div>

        <UButton
          icon="i-lucide-refresh-cw"
          color="neutral"
          variant="outline"
          :loading="loading"
          @click="refreshCart(true)"
        >
          Обновить
        </UButton>
      </div>
    </template>

    <div class="space-y-6">
      <section>
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-base font-semibold">Ожидают оплаты</h3>
          <UBadge color="warning" variant="subtle">{{ heldBookings.length }}</UBadge>
        </div>

        <UAlert
          v-if="hasHeldBookings"
          color="warning"
          variant="subtle"
          title="Нужно подтвердить бронь"
          description="Сначала подтвердите удержанные места. После этого откроется QR-код брони."
        />

        <UAlert
          v-else-if="hasBookedBookings"
          color="success"
          variant="subtle"
          title="Бронь уже подтверждена"
          description="Удержаний больше нет. QR-код можно открыть по кнопке ниже."
        />

        <UAlert
          v-else
          color="neutral"
          variant="subtle"
          title="Корзина пока пустая"
          description="Нажмите на свободные места в схеме, чтобы удержать их и затем подтвердить бронь."
        />

        <div v-if="hasHeldBookings" class="mt-4 space-y-3">
          <div
            v-for="booking in heldBookings"
            :key="booking.id"
            class="rounded-xl border border-gray-200 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium">
                  {{ booking.seat.section }}, ряд {{ booking.seat.row }}, место {{ booking.seat.number }}
                </p>
                <p v-if="!eventId" class="text-sm text-gray-500">
                  {{ booking.event_title || `Событие #${booking.event}` }}
                </p>
                <p class="text-sm text-gray-500">
                  Удержание до {{ formatDateTime(booking.expires_at) }}
                </p>
              </div>

              <div class="text-right">
                <p class="font-semibold">{{ formatPrice(booking.price_snapshot) }}</p>
                <UButton
                  size="sm"
                  color="error"
                  variant="ghost"
                  :loading="bookingStore.isBookingActionPending(booking.id)"
                  @click="release(booking.id)"
                >
                  Убрать
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section v-if="bookedBookings.length">
        <div class="mb-3 flex items-center justify-between">
          <h3 class="text-base font-semibold">Уже подтверждено</h3>
          <UBadge color="success" variant="subtle">{{ bookedBookings.length }}</UBadge>
        </div>

        <div class="space-y-3">
          <div
            v-for="booking in bookedBookings"
            :key="booking.id"
            class="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium">
                  {{ booking.seat.section }}, ряд {{ booking.seat.row }}, место {{ booking.seat.number }}
                </p>
                <p v-if="!eventId" class="text-sm text-emerald-700">
                  {{ booking.event_title || `Событие #${booking.event}` }}
                </p>
                <p class="text-sm text-emerald-700">
                  Бронь подтверждена
                </p>
              </div>

              <div class="text-right">
                <p class="font-semibold">{{ formatPrice(booking.price_snapshot) }}</p>
                <UButton
                  size="sm"
                  color="error"
                  variant="ghost"
                  :loading="bookingStore.isBookingActionPending(booking.id)"
                  @click="openBookedCancellationDialog(booking)"
                >
                  Убрать
                </UButton>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <template #footer>
      <div class="space-y-4">
        <div class="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p class="text-sm text-gray-500">{{ summaryLabel }}</p>
            <p class="text-2xl font-semibold">{{ formatPrice(summaryTotal) }}</p>
            <p v-if="hasHeldBookings" class="text-sm text-amber-700">
              Сначала подтвердите бронь, затем откроется QR-код.
            </p>
            <p v-else-if="hasBookedBookings" class="text-sm text-emerald-700">
              Бронь уже подтверждена. QR-код доступен в любое время.
            </p>
          </div>

          <div class="flex flex-col gap-2 sm:items-end">
            <UButton
              v-if="hasHeldBookings"
              color="primary"
              icon="i-lucide-shield-check"
              :loading="bookingStore.confirmingForEvent(props.eventId)"
              @click="confirmHeldSeats"
            >
              Подтвердить бронь
            </UButton>

            <UButton
              v-else-if="hasBookedBookings"
              color="primary"
              icon="i-lucide-qr-code"
              @click="openCheckoutDialog"
            >
              Перейти к оплате
            </UButton>
          </div>
        </div>

        <div v-if="bookedBookings.length" class="text-sm text-gray-500">
          Подтверждено на сумму {{ formatPrice(bookedTotal) }}.
        </div>
      </div>
    </template>
  </UCard>

  <UModal v-model:open="checkoutOpen" title="QR-код брони">
    <template #body>
      <div class="space-y-4">
        <div class="qr-placeholder">
          <div class="qr-pattern" />
        </div>

        <p class="text-sm text-gray-600">
          Это заглушка QR-кода. После подтверждения брони откройте его и покажите на входе или
          используйте для дальнейшего шага оплаты, если он нужен.
        </p>

        <div v-if="bookedBookings.length" class="rounded-xl bg-gray-50 p-4 text-sm text-gray-600">
          <p class="font-medium text-gray-900">Подтвержденные места</p>
          <ul class="mt-2 space-y-1">
            <li
              v-for="booking in bookedBookings"
              :key="`qr-${booking.id}`"
            >
              {{ booking.seat.section }}, ряд {{ booking.seat.row }}, место {{ booking.seat.number }}
            </li>
          </ul>
        </div>
      </div>
    </template>

    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        @click="checkoutOpen = false"
      >
        Закрыть
      </UButton>
    </template>
  </UModal>

  <UModal v-model:open="bookedCancellationOpen" title="Удалить подтвержденную бронь?">
    <template #body>
      <div class="space-y-3">
        <p class="text-sm text-gray-600">
          Подтвержденное место будет снято, и оно снова станет доступно для бронирования.
        </p>

        <div
          v-if="bookingPendingCancellation"
          class="rounded-xl border border-red-200 bg-red-50/60 p-4 text-sm text-red-900"
        >
          {{ bookingPendingCancellation.seat.section }}, ряд {{ bookingPendingCancellation.seat.row }},
          место {{ bookingPendingCancellation.seat.number }}
        </div>
      </div>
    </template>

    <template #footer>
      <UButton
        color="neutral"
        variant="outline"
        @click="closeBookedCancellationDialog"
      >
        Оставить
      </UButton>

      <UButton
        color="error"
        :loading="bookingPendingCancellation ? bookingStore.isBookingActionPending(bookingPendingCancellation.id) : false"
        @click="cancelBookedBooking"
      >
        Удалить бронь
      </UButton>
    </template>
  </UModal>
</template>

<script setup>
const props = defineProps({
  eventId: {
    type: [String, Number],
    default: null,
  },
  title: {
    type: String,
    default: 'Корзина',
  },
})

const emit = defineEmits(['changed'])

const bookingStore = useBookingStore()
const toast = useToast()

const checkoutOpen = ref(false)
const bookedCancellationOpen = ref(false)
const bookingPendingCancellation = ref(null)
const defaultPaymentReference = 'QR-SIMA-DEMO'

const loading = computed(() => bookingStore.loadingForEvent(props.eventId))
const heldBookings = computed(() => bookingStore.heldBookingsForEvent(props.eventId))
const bookedBookings = computed(() => bookingStore.bookedBookingsForEvent(props.eventId))
const heldTotal = computed(() => bookingStore.heldTotalForEvent(props.eventId))
const bookedTotal = computed(() => bookingStore.bookedTotalForEvent(props.eventId))
const hasHeldBookings = computed(() => heldBookings.value.length > 0)
const hasBookedBookings = computed(() => bookedBookings.value.length > 0)
const summaryLabel = computed(() => {
  if (hasHeldBookings.value) return 'Итого к оплате'
  if (hasBookedBookings.value) return 'Подтверждено на сумму'
  return 'Итого к оплате'
})
const summaryTotal = computed(() => {
  if (hasHeldBookings.value) return heldTotal.value
  if (hasBookedBookings.value) return bookedTotal.value
  return heldTotal.value
})

function formatPrice(value) {
  const amount = Number.parseFloat(value ?? 0)
  return `${new Intl.NumberFormat('ru-RU').format(Number.isFinite(amount) ? amount : 0)} ₽`
}

function formatDateTime(value) {
  if (!value) return 'без ограничения'

  return new Intl.DateTimeFormat('ru-RU', {
    day: '2-digit',
    month: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

async function refreshCart(showToast = false) {
  try {
    await bookingStore.fetchBookings({
      eventId: props.eventId,
      force: true,
      statuses: ['held', 'booked'],
      activeOnly: true,
    })
    emit('changed')

    if (showToast) {
      toast.add({
        title: 'Корзина обновлена',
        description: 'Синхронизировали брони с сервером.',
        color: 'success',
      })
    }
  } catch (err) {
    toast.add({
      title: 'Не удалось обновить корзину',
      description: err?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  }
}

async function release(bookingId) {
  try {
    await bookingStore.releaseBooking({ eventId: props.eventId, bookingId })
    emit('changed')
    toast.add({
      title: 'Место убрано',
      description: 'Удержание снято, место снова доступно другим пользователям.',
      color: 'success',
    })
  } catch (err) {
    toast.add({
      title: 'Не удалось снять удержание',
      description: err?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  }
}

function openBookedCancellationDialog(booking) {
  bookingPendingCancellation.value = booking
  bookedCancellationOpen.value = true
}

function closeBookedCancellationDialog() {
  bookedCancellationOpen.value = false
  bookingPendingCancellation.value = null
}

async function cancelBookedBooking() {
  if (!bookingPendingCancellation.value) return

  try {
    await bookingStore.releaseBooking({
      eventId: props.eventId,
      bookingId: bookingPendingCancellation.value.id,
    })
    closeBookedCancellationDialog()
    emit('changed')
    toast.add({
      title: 'Подтвержденная бронь удалена',
      description: 'Место снова доступно для бронирования.',
      color: 'success',
    })
  } catch (err) {
    toast.add({
      title: 'Не удалось удалить бронь',
      description: err?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  }
}

async function confirmHeldSeats() {
  if (!hasHeldBookings.value) return

  try {
    await bookingStore.confirmHeldBookings({
      eventId: props.eventId,
      bookingIds: heldBookings.value.map((booking) => booking.id),
      paymentReference: defaultPaymentReference,
    })

    emit('changed')
    openCheckoutDialog()
    toast.add({
      title: 'Бронь подтверждена',
      description: 'Места закреплены за вами.',
      color: 'success',
    })
  } catch (err) {
    toast.add({
      title: 'Подтверждение не удалось',
      description: err?.message ?? 'Попробуйте ещё раз.',
      color: 'error',
    })
  }
}

function openCheckoutDialog() {
  checkoutOpen.value = true
}

onMounted(() => {
  void bookingStore.fetchBookings({
    eventId: props.eventId,
    statuses: ['held', 'booked'],
    activeOnly: true,
  })
})

watch(() => props.eventId, () => {
  void bookingStore.fetchBookings({
    eventId: props.eventId,
    force: true,
    statuses: ['held', 'booked'],
    activeOnly: true,
  })
})
</script>

<style scoped>
.qr-placeholder {
  display: flex;
  justify-content: center;
  padding: 1.5rem;
  border: 1px dashed #9ca3af;
  border-radius: 1rem;
  background:
    linear-gradient(135deg, rgba(20, 83, 45, 0.08), rgba(30, 64, 175, 0.08));
}

.qr-pattern {
  width: 180px;
  height: 180px;
  border-radius: 1rem;
  background:
    linear-gradient(90deg, #111827 10px, transparent 10px) 0 0 / 30px 30px,
    linear-gradient(#111827 10px, transparent 10px) 0 0 / 30px 30px,
    linear-gradient(90deg, transparent 20px, #111827 20px) 0 0 / 30px 30px,
    linear-gradient(transparent 20px, #111827 20px) 0 0 / 30px 30px,
    #f9fafb;
  box-shadow: inset 0 0 0 12px #f9fafb;
}
</style>
