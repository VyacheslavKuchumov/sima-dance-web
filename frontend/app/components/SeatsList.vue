<template>
  <UContainer>
    {{ selectedSeat }}
    <!-- show loader while fetching -->
    <UProgress v-if="pending" animation="swing" />
    <DraggableContainer label="План зала" class="max-h-100" v-else>
      
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
                      'seat-unavailable': seatStatus(seat) === 'unavailable'
                    }"
                    @click="onSeatClick(seat)"
                  >
                    <span class="seat-number">{{ seat.number }}</span>
                  </div>

                  <div class="seat-price" v-if="seat.price">
                    {{ seat.price }}₽
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

        <!-- optional: show selected seat -->
        <!-- <div class="selected-info" v-if="selectedSeat">
          Selected: Section <b>{{ selectedSeat.section }}</b>,
          Row <b>{{ selectedSeat.row }}</b>,
          Seat <b>{{ selectedSeat.number }}</b>
          — {{ selectedSeat.price ?? 'no price' }}
        </div> -->
      
    </DraggableContainer>
  </UContainer>
</template>

<script setup>


const props = defineProps({
  event_id: Number,
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





// --- use composable ---
const {
  groupedSeats,
  sortedRowKeys,
  selectedSeat,
  seatStatus,
  isCurrentUserSeat,
  onSeatClick
} = useVenueSeats(seats, currentUserId)

</script>

<style scoped>
.venue-plan {
  display: block;
  gap: 1.5rem;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
}
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
