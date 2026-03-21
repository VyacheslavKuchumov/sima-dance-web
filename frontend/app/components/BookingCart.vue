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

        <div v-if="heldBookings.length" class="space-y-3">
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

        <UAlert
          v-else
          color="neutral"
          variant="subtle"
          title="Корзина пока пустая"
          description="Нажмите на свободные места в схеме, чтобы удержать их и перейти к оплате."
        />
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

              <p class="font-semibold">{{ formatPrice(booking.price_snapshot) }}</p>
            </div>
          </div>
        </div>
      </section>
    </div>

    <template #footer>
      <div class="space-y-4">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm text-gray-500">Итого к оплате</p>
            <p class="text-2xl font-semibold">{{ formatPrice(heldTotal) }}</p>
          </div>

          <UModal v-model:open="checkoutOpen" title="Оплата по QR" :ui="{ footer: 'justify-between' }">
            <UButton
              color="primary"
              icon="i-lucide-qr-code"
              :disabled="!heldBookings.length"
            >
              Перейти к оплате
            </UButton>

            <template #body>
              <div class="space-y-4">
                <div class="qr-placeholder">
                  <div class="qr-pattern" />
                </div>

                <p class="text-sm text-gray-600">
                  Здесь будет ваш QR-код для оплаты. Пока это заглушка: после сканирования и оплаты
                  нажмите кнопку подтверждения ниже.
                </p>

                <UFormField label="Комментарий к оплате">
                  <UInput
                    v-model="paymentReference"
                    class="w-full"
                    placeholder="Например: QR-SIMA-DEMO"
                  />
                </UFormField>
              </div>
            </template>

            <template #footer>
              <UButton
                color="neutral"
                variant="outline"
                @click="checkoutOpen = false"
              >
                Вернуться
              </UButton>

              <UButton
                color="primary"
                :loading="bookingStore.confirmingForEvent(props.eventId)"
                :disabled="!heldBookings.length"
                @click="confirmHeldSeats"
              >
                Я оплатил, подтвердить бронь
              </UButton>
            </template>
          </UModal>
        </div>

        <div v-if="bookedBookings.length" class="text-sm text-gray-500">
          Подтверждено на сумму {{ formatPrice(bookedTotal) }}.
        </div>
      </div>
    </template>
  </UCard>
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
const paymentReference = ref('QR-SIMA-DEMO')

const loading = computed(() => bookingStore.loadingForEvent(props.eventId))
const heldBookings = computed(() => bookingStore.heldBookingsForEvent(props.eventId))
const bookedBookings = computed(() => bookingStore.bookedBookingsForEvent(props.eventId))
const heldTotal = computed(() => bookingStore.heldTotalForEvent(props.eventId))
const bookedTotal = computed(() => bookingStore.bookedTotalForEvent(props.eventId))

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

async function confirmHeldSeats() {
  if (!heldBookings.value.length) return

  try {
    await bookingStore.confirmHeldBookings({
      eventId: props.eventId,
      bookingIds: heldBookings.value.map((booking) => booking.id),
      paymentReference: paymentReference.value || 'QR-SIMA-DEMO',
    })

    checkoutOpen.value = false
    emit('changed')
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
