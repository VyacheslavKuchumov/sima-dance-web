<template>
  <UCard class="w-full">
    <template #header>
      <div class="flex items-center justify-between gap-3">
        <div>
          <h2 class="text-xl font-semibold">{{ title }}</h2>
          <p class="text-sm text-muted">
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
          title="Пока нет броней"
          description="Нажмите на свободные места в схеме, чтобы удержать их и затем подтвердить бронь."
        />

        <div v-if="hasHeldBookings" class="mt-4 space-y-3">
          <div
            v-for="booking in heldBookings"
            :key="booking.id"
            class="rounded-xl border border-default p-4"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium">
                  {{ booking.seat.section }}, ряд {{ booking.seat.row }}, место {{ booking.seat.number }}
                </p>
                <p v-if="!eventId" class="text-sm text-muted">
                  {{ booking.event_title || `Событие #${booking.event}` }}
                </p>
                <p class="text-sm text-muted">
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
            class="rounded-xl border border-emerald-200 bg-emerald-50/60 p-4 dark:border-emerald-800 dark:bg-emerald-950/30"
          >
            <div class="flex items-start justify-between gap-3">
              <div>
                <p class="font-medium">
                  {{ booking.seat.section }}, ряд {{ booking.seat.row }}, место {{ booking.seat.number }}
                </p>
                <p v-if="!eventId" class="text-sm text-emerald-700 dark:text-emerald-300">
                  {{ booking.event_title || `Событие #${booking.event}` }}
                </p>
                <p class="text-sm text-emerald-700 dark:text-emerald-300">
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
            <p class="text-sm text-muted">{{ summaryLabel }}</p>
            <p class="text-2xl font-semibold">{{ formatPrice(summaryTotal) }}</p>
            <p v-if="hasHeldBookings" class="text-sm text-amber-700 dark:text-amber-300">
              Сначала подтвердите бронь, затем откроется QR-код.
            </p>
            <p v-else-if="hasBookedBookings" class="text-sm text-emerald-700 dark:text-emerald-300">
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

        <div v-if="bookedBookings.length" class="text-sm text-muted">
          Подтверждено на сумму {{ formatPrice(bookedTotal) }}.
        </div>

        <UAlert
          v-if="bookedBookings.length"
          color="info"
          variant="subtle"
          title="После оплаты отправьте подтверждение"
          description="Пожалуйста, после оплаты отправьте подтверждение об оплате в мессенджере."
        />
      </div>
    </template>
  </UCard>

  <UModal v-model:open="checkoutOpen" title="QR-код брони">
    <template #body>
      <div class="space-y-4">
        <div class="qr-placeholder">
          <img
            v-if="qrCodeDataUrl"
            :src="qrCodeDataUrl"
            alt="QR-код для оплаты брони"
            class="qr-image"
          >

          <div v-else-if="qrCodeLoading" class="qr-status text-sm text-toned">
            Подготавливаем QR-код...
          </div>

          <div v-else class="qr-status text-sm text-error">
            {{ qrCodeError || 'Не удалось подготовить QR-код.' }}
          </div>
        </div>

        <p class="text-sm text-toned">
          Отсканируйте QR-код для оплаты или откройте ссылку вручную, если удобнее.
        </p>

        <div
          v-if="bookedBookings.length"
          class="rounded-xl border border-primary/20 bg-primary/5 p-4"
        >
          <p class="text-sm text-muted">Сумма к оплате</p>
          <p class="text-2xl font-semibold">{{ formatPrice(bookedTotal) }}</p>
        </div>

        <UButton
          color="primary"
          variant="soft"
          icon="i-lucide-external-link"
          :to="paymentUrl"
          target="_blank"
          rel="noopener noreferrer"
        >
          Открыть ссылку оплаты
        </UButton>

        <div v-if="bookedBookings.length" class="rounded-xl bg-elevated p-4 text-sm text-toned">
          <p class="font-semibold">Подтвержденные места</p>
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
        <p class="text-sm text-toned">
          Подтвержденное место будет снято, и оно снова станет доступно для бронирования.
        </p>

        <div
          v-if="bookingPendingCancellation"
          class="rounded-xl border border-red-200 bg-red-50/60 p-4 text-sm text-red-900 dark:border-red-800 dark:bg-red-950/30 dark:text-red-100"
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
    default: 'Мои брони',
  },
})

const emit = defineEmits(['changed'])

const bookingStore = useBookingStore()
const toast = useAppToast()

const checkoutOpen = ref(false)
const bookedCancellationOpen = ref(false)
const bookingPendingCancellation = ref(null)
const defaultPaymentReference = 'QR-SIMA-DEMO'
const paymentUrl = 'https://payment.alfabank.ru/sc/TzMfqhRHpufumcmu'
const qrCodeDataUrl = ref('')
const qrCodeLoading = ref(false)
const qrCodeError = ref('')

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
        title: 'Мои брони обновлены',
        description: 'Синхронизировали брони с сервером.',
        color: 'success',
      })
    }
  } catch (err) {
    toast.add({
      title: 'Не удалось обновить брони',
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
  void ensurePaymentQrCode()
}

async function ensurePaymentQrCode() {
  if (qrCodeDataUrl.value || qrCodeLoading.value) return

  qrCodeLoading.value = true
  qrCodeError.value = ''

  try {
    const { toDataURL } = await import('qrcode')
    qrCodeDataUrl.value = await toDataURL(paymentUrl, {
      width: 220,
      margin: 1,
      color: {
        dark: '#111827',
        light: '#FFFFFF',
      },
    })
  } catch (error) {
    console.error('Failed to generate payment QR code', error)
    qrCodeError.value = 'QR-код временно недоступен.'
  } finally {
    qrCodeLoading.value = false
  }
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
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  min-height: 240px;
  border: 1px solid rgba(17, 24, 39, 0.1);
  border-radius: 1rem;
  background:
    radial-gradient(circle at top left, rgba(20, 83, 45, 0.08), transparent 55%),
    radial-gradient(circle at bottom right, rgba(30, 64, 175, 0.08), transparent 55%),
    #f8fafc;
}

.qr-image {
  width: min(220px, 100%);
  height: auto;
  border-radius: 1rem;
  background: #fff;
  box-shadow:
    0 18px 40px rgba(15, 23, 42, 0.12),
    0 0 0 12px rgba(255, 255, 255, 0.9);
}

.qr-status {
  text-align: center;
}
</style>
