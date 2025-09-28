<template>
  <UContainer >
    <!-- show loader while fetching -->
    <UProgress v-if="pending" animation="swing" />
    <DraggableContainer label="План зала" class="max-h-110 md:max-h-150" v-else>
        <div
          v-for="(rows, section) in groupedSeats"
          :key="section"
          class="section-container"
        >
          <h3 class="section-title">{{ section }}</h3>

          <!-- iterate sorted row numbers -->
          <div
            v-for="rowNumber in sortedRowKeys(rows)"
            :key="rowNumber"
            class="row-container"
          >
            <div class="row-label">Ряд {{ rowNumber }}</div>

            <div class="seats-row">
              <!-- render seats and gaps -->
              <div
                v-for="(seat, idx) in rows[rowNumber]"
                :key="seat ? 's-' + seat.id : 'gap-' + idx"
                class="seat-circle-wrapper"
              >
                <template v-if="seat">
                  <div
                    class="seat-circle"
                    :class="{
                      'seat-available': seatStatus(seat) === 'available',
                      'seat-booked': seatStatus(seat) === 'booked' && !isCurrentUserSeat(seat),
                      'seat-booked-current': seatStatus(seat) === 'booked' && isCurrentUserSeat(seat),
                      'seat-selected': selectedSeats.find(s => s.id === seat.id),
                      'seat-unavailable': seatStatus(seat) === 'unavailable'
                    }"
                    @click="onSeatClick(seat)"
                  >
                    <span class="seat-number">{{ seat.number }}</span>
                  </div>

                  <div class="seat-price" v-if="seat.price">
                    {{ parseInt(seat.price) }}₽
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
    <UContainer class="mt-4 flex justify-center">
      <UModal title="Выбранные места" :ui="{ footer: 'justify-end' }">
        <UButton color="primary" variant="solid" size="xl" icon="i-lucide-ticket" v-if="selectedSeats.length > 0" >
          Подтвердить бронь ({{ selectedSeats.length }})
        </UButton>
        
        <template #body>
          <UCard v-for="seat in selectedSeats" :key="seat.id" class="mb-2">
            Секция: {{ seat.section }}, Ряд: {{ seat.row }}, Место: {{ seat.number }}, Цена: {{ seat.price ? parseInt(seat.price) + '₽' : '—' }}

          </UCard>
        </template>
        <template #footer="{ close }">
          <UButton label="Сбросить" color="error" variant="outline" @click="close" />
          <UButton label="Подтвердить" color="primary" />
        </template>
      </UModal>
    </UContainer>
    
  </UContainer>
  

  
  
</template>

<script setup>


const props = defineProps({
  event_id: String,
})

const config = useRuntimeConfig()
const auth = useAuthStore()
// Current user
const currentUserId = auth.user?.id || null

const toast = useToast()

// Fetch seat data
const { data, pending, error } = useFetch(
  `${config.public.BACKEND_URL}/api/booking/events/${props.event_id}/seatmap/`
)

const seats = computed(() => data.value ?? [])

if (error.value) {
  toast.add({
    title: 'Ошибка',
    description: `Не удалось загрузить ${error.value}`,
    color: 'error',
  })
}

function onSeatClick(seat) {
    const status = seatStatus(seat)
    if (status === 'available' || (status === 'booked' && isCurrentUserSeat(seat))) {
        toggleSeatSelection(seat)
    } else {
        toast.add({
          title: 'Место недоступно',
          description: `Это место уже занято.`,
          color: 'warning',
        })
    }
  }





// --- use composable ---
const {
  groupedSeats,
  sortedRowKeys,
  selectedSeats,
  seatStatus,
  isCurrentUserSeat,
  toggleSeatSelection,
} = useVenueSeats(seats, currentUserId)

</script>

<style scoped>

.section-container {
  margin-bottom: 1.75rem;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.75rem;
}
.section-title {
  margin: 0 0 0.5rem 0;
  font-size: 1.05rem;
  color: #222;
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
  color: #444;
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
.seat-price-empty {
  color: #999;
}
.seat-available {
  background: #e6ffed;
  border-color: #49a36b;
  color: #0b4d28;
}
.seat-selected {
  background: #cce5ff;
  border-color: #2a7ae4;
  color: #003380;
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
.selected-info {
  margin-top: 1rem;
  padding: 0.6rem;
  border-radius: 6px;
  background: #fafafa;
  font-size: 0.95rem;
}
</style>
