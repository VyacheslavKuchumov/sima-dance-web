<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Список мест {{ sse() }}
    </v-card-title>
  </v-card>
  
  
  <!-- Main Card with Toolbar -->
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1400">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
      <v-spacer></v-spacer>
    </v-toolbar>
    <v-card max-height="600">
      <!-- Zoomable Container -->
      <div class="zoom-window" ref="zoomContainer">
        <div class="pan-zoom-area">
          <v-container
            v-if="seats_in_events() && seats_in_events().length"
            class="venue-layout"
          >
            <!-- Venue plan content: Sections, rows, and seats -->
            <div
              v-for="(rows, section) in groupedSeats"
              :key="section"
              class="section-container"
            >
              <h3>{{ section }}</h3>
              <div
                v-for="rowNumber in sortedRowKeys(rows)"
                :key="rowNumber"
                class="row-container"
              >
                <div class="row-label">{{ rowNumber }}</div>
                <div class="seats-row">
                  <v-btn
                    v-for="seat in rows[rowNumber]"
                    :key="seat.seat_id"
                    class="seat"
                    :class="{
                      'seat-available': seat.status === 'available',
                      'seat-held': seat.status === 'held',
                      'seat-booked': seat.status === 'booked' && !isCurrentUserSeat(seat),
                      'seat-booked-current': seat.status === 'booked' && isCurrentUserSeat(seat),
                      'seat-unavailable': seat.status === 'unavailable'
                    }"
                    @click="bookSeat(seat)"
                    :disabled="seat.status === 'unavailable' || seat.status === 'held' || seat.status === 'booked' && !isCurrentUserSeat(seat)"
                  >
                    <div class="seat-top">
                      <span class="seat-number">{{ seat.seat.number }}</span>
                      <v-icon small>mdi-seat</v-icon>
                    </div>
                    <div class="seat-bottom">
                      <span class="seat-price">{{ seat.price }}р</span>
                    </div>
                  </v-btn>
                </div>
              </div>
            </div>
          </v-container>
          <v-alert v-else type="info" class="ma-4">
            Администратор не инициализировал места
          </v-alert>
        </div>
      </div>
    </v-card>
  </v-card>

  <!-- Dialog for Creating/Editing a Seat -->
  <v-dialog v-model="bookingDialog" persistent max-width="450px">
    <v-card>
      <v-card-title class="text-h5 text-wrap">
        Подтверждение бронирования
      </v-card-title>
      <v-card-text>
        Вы уверены, что хотите забронировать место?
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" @click="cancelBooking">Отмена</v-btn>
        <v-btn color="primary" @click="saveBooking">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex";
import panzoom from "panzoom"; // Install via npm: npm install panzoom


export default {
  data() {
    return {
      overlay: false,
      bookingDialog: false,
      bookingData: null,
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
      panzoomInstance: null,
    };
  },
  computed: {
    // Group seats by section and then by row
    groupedSeats() {
      const groups = {};
      this.seats_in_events().forEach((seatInEvent) => {
        const section = seatInEvent.seat.section;
        const row = seatInEvent.seat.row;
        if (!groups[section]) {
          groups[section] = {};
        }
        if (!groups[section][row]) {
          groups[section][row] = [];
        }
        groups[section][row].push(seatInEvent);
      });
      console.log(groups);
      return groups;
    },
  },
  methods: {
    sse() {
      return this.$store.state.sse.data;
    },
    user() {
      return this.$store.state.user.user;
    },
    seats_in_events() {
      return this.$store.state.seats_in_events.data || [];
    },
    // Helper method to sort row keys in descending order
    sortedRowKeys(rows) {
      return Object.keys(rows).sort((a, b) => Number(b) - Number(a));
    },
    // Check if the seat belongs to the current user
    isCurrentUserSeat(seat) {
      if (this.user()) {
        return seat.booking && seat.booking.user_uid === this.$store.state.user.user.user_uid;
      }
      return false;
    },
    ...mapActions({
      initSeatsInEvent: "seats_in_events/initSeatsInEvent",
      getSeatsInEvent: "seats_in_events/getSeatsInEvent",
      createSeatInEvent: "seats_in_events/createSeatInEvent",
      updateSeatInEvent: "seats_in_events/updateSeatInEvent",
      deleteSeatInEvent: "seats_in_events/deleteSeatInEvent",
      
      confirmBooking: "bookings/confirmBooking",
      createBooking: "bookings/createBooking",
      deleteBooking: "bookings/deleteBooking",
      
      getUser: "user/getUserByUid",

      startListeningToBookingUpdates: "sse/startListeningToBookingUpdates",
    }),
    goBack() {
      this.$router.go(-1);
    },
    async bookSeat(item) {
      try {
        this.overlay = true;
        const data = {
          user_uid: this.$store.state.user.user.user_uid,
          seat_in_event_id: item.seat_in_event_id,
        };
        // Capture the booking response
        const bookingResponse = await this.createBooking(data);
        // Refresh the seat data
        await this.getSeatsInEvent(this.$route.params.uid);
        // Try to locate the updated seat that should now include booking info
        const updatedSeat = this.seats_in_events().find(
          (seat) => seat.seat_in_event_id === item.seat_in_event_id
        );
        // If updatedSeat has booking details, use it; otherwise, merge the response
        if (updatedSeat && updatedSeat.booking) {
          this.bookingData = updatedSeat;
        } else {
          this.bookingData = { ...item, booking: bookingResponse };
        }
        this.bookingDialog = true;
      } catch (error) {
        console.error("Error booking seat:", error);
      } finally {
        this.overlay = false;
      }
    },
    async cancelBooking() {
      try {
        this.overlay = true;
        // Use the booking ID from the bookingData
        const bookingId = this.bookingData?.booking?.booking_id;
        if (!bookingId) {
          throw new Error("Booking ID not found.");
        }
        await this.deleteBooking(bookingId);
        await this.getSeatsInEvent(this.$route.params.uid);
        this.bookingDialog = false;
      } catch (error) {
        console.error("Error cancelling booking:", error);
      } finally {
        this.overlay = false;
      }
    },
    async saveBooking() {
      try {
        this.overlay = true;
        const bookingId = this.bookingData?.booking?.booking_id;
        if (!bookingId) {
          throw new Error("Booking ID not found.");
        }
        await this.confirmBooking(bookingId);
        await this.getSeatsInEvent(this.$route.params.uid);
        this.bookingDialog = false;
      } catch (error) {
        console.error("Error confirming booking:", error);
      } finally {
        this.overlay = false;
      }
    },
  },
  async created() {
    const eventUid = this.$route.params.uid;
    this.overlay = true;
    await this.getSeatsInEvent(eventUid);
    this.uid = localStorage.getItem("uid");
    if (this.uid) {
      await this.getUser();
    }

    this.overlay = false;

  },
  async mounted() {
    
    
    // Initialize panzoom on the zoom container for panning and zooming
    this.panzoomInstance = panzoom(this.$refs.zoomContainer, {
      maxZoom: 3,
      minZoom: 0.5,
      smoothScroll: true,
      bounds: true,
      boundsPadding: 0.5,
    });
    await this.startListeningToBookingUpdates();
  },
  beforeDestroy() {
    if (this.panzoomInstance) {
      this.panzoomInstance.dispose();
    }
  },
};
</script>

<style scoped>
.zoom-window {
  width: 1900px;      /* Visible window width */
  height: 2100px;     /* Visible window height */
  overflow: hidden;
  border: 1px solid #ccc;
  margin: 20px auto;
  position: relative;
}

.pan-zoom-area {
  width: 1800px;
  height: 2100px;
}

/* Venue layout and plan styling */
.venue-layout {
  padding: 20px;
}

/* Section container for each seating area */
.section-container {
  margin-bottom: 30px;
  border: 1px solid #ccc;
  padding: 10px;
}

/* Each row in a section */
.row-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

/* Left side row label */
.row-label {
  width: 40px;
  text-align: right;
  margin-right: 10px;
  font-weight: bold;
}

/* Container for the seats in a row */
.seats-row {
  display: flex;
}

/* Updated seat styling */
.seat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 60px;
  height: 60px;
  margin-right: 5px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: border 0.2s;
}

.seat:hover {
  border: 1px solid #888;
}

/* Seat top row: number and icon */
.seat-top {
  display: flex;
  align-items: center;
  width: 100%;
}

/* Seat number styling: positioned to the left */
.seat-number {
  font-size: 10px;
  margin-right: 2px;
  white-space: nowrap;
}

/* Price styling: beneath the icon */
.seat-bottom {
  font-size: 10px;
  margin-top: 2px;
}

/* Color coding for seat status */
/* Blue: Available Seats */
.seat-available {
  color: #428af5;
}

/* For seats held by others (if needed) */
.seat-held {
  color: orange;
}

/* Orange: Current User's Held Seats */
.seat-held-current {
  color: orange;
}

/* Red: Other Users' Booked Seats */
.seat-booked {
  color: red;
}

/* Green: Current User's Booked Seats */
.seat-booked-current {
  color: green;
}

/* Gray: Unavailable Seats */
.seat-unavailable {
  color: gray;
}
</style>
