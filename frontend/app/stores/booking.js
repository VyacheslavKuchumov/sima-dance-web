function normalizeBookings(payload) {
  if (Array.isArray(payload)) return payload
  if (Array.isArray(payload?.results)) return payload.results
  return []
}

function toEventKey(eventId) {
  return eventId == null || eventId === '' ? 'all' : String(eventId)
}

function toPriceNumber(value) {
  const parsed = Number.parseFloat(value ?? 0)
  return Number.isFinite(parsed) ? parsed : 0
}

function normalizeUserId(value) {
  const parsed = Number(value)
  return Number.isFinite(parsed) && parsed > 0 ? parsed : null
}

function cacheKeysForEvent(state, eventId) {
  const keys = [toEventKey(eventId)]

  if (Object.prototype.hasOwnProperty.call(state.bookingsByEvent, 'all')) {
    keys.push('all')
  }

  return [...new Set(keys)]
}

function normalizeRealtimeBooking({ booking, seat }) {
  if (!booking?.id || !seat?.id) return null

  return {
    id: booking.id,
    user: booking.user ?? null,
    user_id: booking.user_id ?? null,
    user_details: booking.user_details ?? null,
    seat: {
      id: seat.id,
      section: seat.section,
      row: seat.row,
      number: seat.number,
      available: seat.available,
      price: seat.price ?? null,
    },
    event: booking.event_id,
    event_title: booking.event_title ?? null,
    status: booking.status,
    created_at: booking.created_at ?? booking.updated_at ?? null,
    updated_at: booking.updated_at ?? null,
    expires_at: booking.expires_at ?? null,
    price_snapshot: booking.price_snapshot ?? seat.price ?? null,
    is_paid: Boolean(booking.is_paid),
    is_ticket_issued: Boolean(booking.is_ticket_issued),
  }
}

function isActiveHeldBooking(booking) {
  if (booking?.status !== 'held') return false
  if (!booking.expires_at) return true
  return new Date(booking.expires_at).getTime() > Date.now()
}

const inflightFetches = new Map()

export const useBookingStore = defineStore('booking', {
  state: () => ({
    bookingsByEvent: {},
    loadingByEvent: {},
    actionByBookingId: {},
    confirmingByEvent: {},
  }),

  getters: {
    bookingsForEvent: (state) => (eventId) => {
      return state.bookingsByEvent[toEventKey(eventId)] ?? []
    },

    loadingForEvent: (state) => (eventId) => {
      return Boolean(state.loadingByEvent[toEventKey(eventId)])
    },

    heldBookingsForEvent() {
      return (eventId) => this.bookingsForEvent(eventId).filter(isActiveHeldBooking)
    },

    bookedBookingsForEvent() {
      return (eventId) => this.bookingsForEvent(eventId).filter((booking) => booking.status === 'booked')
    },

    heldBookingMapForEvent() {
      return (eventId) => {
        return this.heldBookingsForEvent(eventId).reduce((map, booking) => {
          map[booking.seat.id] = booking
          return map
        }, {})
      }
    },

    heldTotalForEvent() {
      return (eventId) => this.heldBookingsForEvent(eventId)
        .reduce((sum, booking) => sum + toPriceNumber(booking.price_snapshot), 0)
    },

    bookedTotalForEvent() {
      return (eventId) => this.bookedBookingsForEvent(eventId)
        .reduce((sum, booking) => sum + toPriceNumber(booking.price_snapshot), 0)
    },

    confirmingForEvent: (state) => (eventId) => {
      return Boolean(state.confirmingByEvent[toEventKey(eventId)])
    },

    isBookingActionPending: (state) => (bookingId) => {
      return Boolean(state.actionByBookingId[String(bookingId)])
    },
  },

  actions: {
    setEventBookings(eventId, bookings) {
      this.bookingsByEvent[toEventKey(eventId)] = bookings
    },

    removeBooking(eventId, bookingId) {
      for (const eventKey of cacheKeysForEvent(this, eventId)) {
        const current = this.bookingsByEvent[eventKey] ?? []
        this.bookingsByEvent[eventKey] = current.filter((item) => item.id !== bookingId)
      }
    },

    upsertBooking(eventId, booking) {
      for (const eventKey of cacheKeysForEvent(this, eventId)) {
        const current = [...(this.bookingsByEvent[eventKey] ?? [])]
        const index = current.findIndex((item) => item.id === booking.id)

        if (index === -1) {
          current.unshift(booking)
        } else {
          current.splice(index, 1, booking)
        }

        this.bookingsByEvent[eventKey] = current
      }
    },

    applyRealtimeBookingChange({ eventId, action, booking, seat, currentUserId } = {}) {
      const normalizedCurrentUserId = normalizeUserId(currentUserId)
      const normalizedBookingUserId = normalizeUserId(booking?.user_id)
      const normalizedEventId = booking?.event_id ?? eventId
      const normalizedBooking = normalizeRealtimeBooking({ booking, seat })

      if (!normalizedBooking?.id || !normalizedEventId) return

      if (normalizedCurrentUserId == null || normalizedBookingUserId !== normalizedCurrentUserId) {
        if (action === 'deleted') {
          this.removeBooking(normalizedEventId, normalizedBooking.id)
        }
        return
      }

      if (action === 'deleted') {
        this.removeBooking(normalizedEventId, normalizedBooking.id)
        return
      }

      if (!['held', 'booked'].includes(normalizedBooking.status)) {
        this.removeBooking(normalizedEventId, normalizedBooking.id)
        return
      }

      this.upsertBooking(normalizedEventId, normalizedBooking)
    },

    async fetchEventBookings({ eventId, force = false, status = 'held,booked', activeOnly = true } = {}) {
      const auth = useAuthStore()
      const ok = await auth.ensureAccessToken()

      if (!ok) return []

      const requestKey = `${toEventKey(eventId)}:${status}:${activeOnly}`
      if (!force && inflightFetches.has(requestKey)) {
        return inflightFetches.get(requestKey)
      }

      const request = (async () => {
        this.loadingByEvent[toEventKey(eventId)] = true

        try {
          const payload = await $fetch('/api/backend/booking/bookings/', {
            headers: auth.authHeader(),
            query: {
              ...(eventId ? { event_id: eventId } : {}),
              status,
              active_only: activeOnly ? 'true' : 'false',
            },
          })

          const bookings = normalizeBookings(payload)
          this.setEventBookings(eventId, bookings)
          return bookings
        } finally {
          this.loadingByEvent[toEventKey(eventId)] = false
          inflightFetches.delete(requestKey)
        }
      })()

      inflightFetches.set(requestKey, request)
      return request
    },

    async fetchBookings({ eventId = null, force = false, statuses = ['held', 'booked'], activeOnly = true } = {}) {
      const status = Array.isArray(statuses) ? statuses.join(',') : statuses
      return this.fetchEventBookings({ eventId, force, status, activeOnly })
    },

    async holdSeat({ eventId, seatId }) {
      const auth = useAuthStore()
      const ok = await auth.ensureAccessToken()

      if (!ok) {
        throw new Error('Нужна авторизация, чтобы удержать место.')
      }

      const booking = await $fetch('/api/backend/booking/hold/', {
        method: 'POST',
        body: {
          event_id: eventId,
          seat_id: seatId,
        },
        headers: auth.authHeader(),
      })

      this.upsertBooking(eventId, booking)
      return booking
    },

    async releaseBooking({ eventId, bookingId }) {
      const auth = useAuthStore()
      const ok = await auth.ensureAccessToken()

      if (!ok) {
        throw new Error('Нужна авторизация, чтобы убрать место из ваших броней.')
      }

      this.actionByBookingId[String(bookingId)] = true

      try {
        const booking = await $fetch(`/api/backend/booking/bookings/${bookingId}/release/`, {
          method: 'POST',
          headers: auth.authHeader(),
        })

        this.removeBooking(eventId, booking.id)
        return booking
      } finally {
        this.actionByBookingId[String(bookingId)] = false
      }
    },

    async confirmHeldBookings({ eventId, bookingIds, paymentReference = 'QR-DEMO' }) {
      const auth = useAuthStore()
      const ok = await auth.ensureAccessToken()

      if (!ok) {
        throw new Error('Нужна авторизация, чтобы подтвердить бронь.')
      }

      this.confirmingByEvent[toEventKey(eventId)] = true

      try {
        const bookings = await $fetch('/api/backend/booking/confirm/', {
          method: 'POST',
          body: {
            booking_ids: bookingIds,
            payment_reference: paymentReference,
          },
          headers: auth.authHeader(),
        })

        for (const booking of bookings) {
          this.upsertBooking(eventId, booking)
        }

        return bookings
      } finally {
        this.confirmingByEvent[toEventKey(eventId)] = false
      }
    },

    heldItemsForEvent(eventId) {
      return this.heldBookingsForEvent(eventId)
    },
  },
})
