<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
  
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Настройка посадки
    </v-card-title>
  </v-card>

  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1400">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
      <v-spacer></v-spacer>
      <v-tooltip :location="location" :origin="origin" no-click-animation>
        <template v-slot:activator="{ props }">
          <v-btn v-bind="props" v-if="seats_in_events().length === 0" icon="mdi-plus-box-multiple" color="primary" @click="initializeSeatsInEvents"></v-btn>
        </template>
        <div>Инициализировать места</div>
      </v-tooltip>
      <v-btn icon="mdi-account-multiple" color="green" @click="goToBookings"></v-btn>
    </v-toolbar>
    <v-card max-height="600">
      <div class="zoom-window" ref="zoomContainer">
        <div class="pan-zoom-area">
          <v-container v-if="seats_in_events() && seats_in_events().length" class="venue-layout">
            <div v-for="(rows, section) in groupedSeats" :key="section" class="section-container">
              <h3>{{ section }}</h3>
              <div v-for="rowNumber in sortedRowKeys(rows)" :key="rowNumber" class="row-container">
                <div class="row-label">{{ rowNumber }}</div>
                <div class="seats-row">
                  <div
                    v-for="(seat, index) in rows[rowNumber]"
                    :key="seat ? seat.seat_id : `gap-${section}-${rowNumber}-${index}`"
                    class="seat-circle-wrapper"
                  >
                    <template v-if="seat">
                      <div
                        class="seat-circle"
                        :class="{
                          'seat-paid': seat.booking?.paid === true,
                          'seat-available': seat.status === 'available',
                          'seat-held': seat.status === 'held',
                          'seat-booked': seat.status === 'booked' && seat.booking?.paid === false,
                          'seat-unavailable': seat.status === 'unavailable',

                        }"
                        @click="openEditDialog(seat); console"
                      >
                        <span class="seat-number">{{ seat.seat.number }}</span>
                      </div>
                      <div class="seat-price">{{ seat.price }}р</div>
                    </template>
                    <template v-else>
                      <div class="seat-gap"></div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </v-container>
          <v-alert v-else type="info" class="ma-4">
            Нет данных
          </v-alert>
        </div>
      </div>
    </v-card>
  </v-card>

  <v-dialog v-model="editDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5">
        Редактировать место
      </v-card-title>
      <v-card-text align="center">
        <p>Секция: <strong>{{ seat()?.seat.section }}</strong></p>
        <p>Место: <strong>{{ seat()?.seat.number }}</strong></p>
        <p>Ряд: <strong>{{ seat()?.seat.row }}</strong></p>
        <p v-if="seat().booking">ФИО родителя: <strong>{{ seat()?.booking?.user.name }}</strong></p>
        <p v-if="seat().booking">ФИО ребенка: <strong>{{ seat()?.booking?.user.child_name }}</strong></p>

        <v-btn
          class="ma-5"
          color="error"
          v-if="seat().booking"
          @click="deleteSeatBooking"
        >
          Удалить бронь
        </v-btn>

        <v-form ref="seatInEventForm" v-model="valid" @submit.prevent="saveSeatInEvent">
          <v-select
            v-if="editingSeatInEvent"
            v-model="seatInEventForm.status"
            label="Статус"
            :items="['available', 'unavailable']"
            :rules="[rules.required]"
            :disabled="editingSeatInEvent.status === 'booked' || editingSeatInEvent.status === 'held'"
          ></v-select>
          <v-text-field
            v-model="seatInEventForm.price"
            label="Цена"
            type="number"
            clearable
            :rules="[rules.required]"
          ></v-text-field>          
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="closeEditDialog">Отмена</v-btn>
        
        <v-btn color="primary" :disabled="!valid" @click="saveSeatInEvent">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex";
import Panzoom from '@panzoom/panzoom'

export default {
  data() {
    return {
      overlay: false,
      editDialog: false,
      editingSeatInEvent: null,
      seatInEventForm: {
        status: "",
        price: null,
      },
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
      panzoomInstance: null,
    };
  },
  computed: {
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

      // Добавляем пропуск между 13-м и 14-м местом в 7 ряду Балкона
      if (groups["Балкон"] && groups["Балкон"]["7"]) {
        let rowSeats = groups["Балкон"]["7"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 13);
        if (index !== -1) {
          // Вставляем null как пропуск после 13-го места
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
          rowSeats.splice(index + 4, 0, null);
          rowSeats.splice(index + 5, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["6"]) {
        let rowSeats = groups["Балкон"]["6"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 12);
        if (index !== -1) {
          // Вставляем null как пропуск после 12-го места
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
          rowSeats.splice(index + 4, 0, null);
          rowSeats.splice(index + 5, 0, null);
          rowSeats.splice(index + 6, 0, null);
          rowSeats.splice(index + 7, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["5"]) {
        let rowSeats = groups["Балкон"]["5"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 12);
        if (index !== -1) {
          // Вставляем null как пропуск после 12-го места
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
          rowSeats.splice(index + 4, 0, null);
          rowSeats.splice(index + 5, 0, null);
          rowSeats.splice(index + 6, 0, null);
          rowSeats.splice(index + 7, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["4"]) {
        let rowSeats = groups["Балкон"]["4"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 12);
        if (index !== -1) {

          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
          rowSeats.splice(index + 4, 0, null);
          rowSeats.splice(index + 5, 0, null);
          rowSeats.splice(index + 6, 0, null);
          rowSeats.splice(index + 7, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["3"]) {
        let rowSeats = groups["Балкон"]["3"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 12);
        if (index !== -1) {

          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
          rowSeats.splice(index + 4, 0, null);
          rowSeats.splice(index + 5, 0, null);
          rowSeats.splice(index + 6, 0, null);
          rowSeats.splice(index + 7, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["2"]) {
        let rowSeats = groups["Балкон"]["2"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 14);
        if (index !== -1) {

          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
        }
      }
      if (groups["Балкон"] && groups["Балкон"]["1"]) {
        let rowSeats = groups["Балкон"]["1"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 14);
        if (index !== -1) {

          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);
        }
      }


      /////


      if (groups["Амфитеатр"] && groups["Амфитеатр"]["17"]) {
        let rowSeats = groups["Амфитеатр"]["17"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 6);
        if (index !== -1) {
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 17, 0, null);
          rowSeats.splice(index + 18, 0, null);
        }
      }

      if (groups["Амфитеатр"] && groups["Амфитеатр"]["16"]) {
        let rowSeats = groups["Амфитеатр"]["16"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 6);
        if (index !== -1) {
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 17, 0, null);
          rowSeats.splice(index + 18, 0, null);
        }
      }
      if (groups["Амфитеатр"] && groups["Амфитеатр"]["15"]) {
        let rowSeats = groups["Амфитеатр"]["15"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 6);
        if (index !== -1) {
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 17, 0, null);
          rowSeats.splice(index + 18, 0, null);
        }
      }
      if (groups["Амфитеатр"] && groups["Амфитеатр"]["14"]) {
        let rowSeats = groups["Амфитеатр"]["14"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 6);
        if (index !== -1) {
          rowSeats.splice(index + 1, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 17, 0, null);
          rowSeats.splice(index + 18, 0, null);
        }
      }

      if (groups["Амфитеатр"] && groups["Амфитеатр"]["13"]) {
        let rowSeats = groups["Амфитеатр"]["13"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 6);
        if (index !== -1) {
          rowSeats.splice(index - 4, 0, null);
          rowSeats.splice(index + 2, 0, null);
          rowSeats.splice(index + 3, 0, null);

          rowSeats.splice(index + 9, 0, null);
          rowSeats.splice(index + 9, 0, null);
          rowSeats.splice(index + 10, 0, null);
          rowSeats.splice(index + 11, 0, null);

          rowSeats.splice(index + 18, 0, null);
          rowSeats.splice(index + 18, 0, null);
        }
      }

      //////

      if (groups["Партер"] && groups["Партер"]["12"]) {
        let rowSeats = groups["Партер"]["12"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["11"]) {
        let rowSeats = groups["Партер"]["11"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["10"]) {
        let rowSeats = groups["Партер"]["10"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["9"]) {
        let rowSeats = groups["Партер"]["9"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["8"]) {
        let rowSeats = groups["Партер"]["8"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["7"]) {
        let rowSeats = groups["Партер"]["7"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["6"]) {
        let rowSeats = groups["Партер"]["6"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["5"]) {
        let rowSeats = groups["Партер"]["5"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["4"]) {
        let rowSeats = groups["Партер"]["4"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["3"]) {
        let rowSeats = groups["Партер"]["3"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);


          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["2"]) {
        let rowSeats = groups["Партер"]["2"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);


          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }
      if (groups["Партер"] && groups["Партер"]["1"]) {
        let rowSeats = groups["Партер"]["1"];
        // Сортируем по номеру места
        rowSeats.sort((a, b) => Number(a.seat.number) - Number(b.seat.number));
        const index = rowSeats.findIndex(seat => Number(seat.seat.number) === 1);
        if (index !== -1) {
          
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);
          rowSeats.splice(index + 0, 0, null);

          rowSeats.splice(index + 14, 0, null);
          rowSeats.splice(index + 14, 0, null);

        }
      }

      return groups;
    },
  },
  methods: {
    
    

    

    seats_in_events() {
      return this.$store.state.seats_in_events.data || [];
    },
    seat(){
      return this.$store.state.seats_in_events.seat_in_event || [];
    },

    sortedRowKeys(rows) {
      return Object.keys(rows).sort((a, b) => Number(b) - Number(a));
    },

    ...mapActions({
      initSeatsInEvent: "seats_in_events/initSeatsInEvent",
      getSeatsInEvent: "seats_in_events/getSeatsInEvent",
      createSeatInEvent: "seats_in_events/createSeatInEvent",
      updateSeatInEvent: "seats_in_events/updateSeatInEvent",
      deleteSeatInEvent: "seats_in_events/deleteSeatInEvent",
      getVenues: "venues/getVenues",
      getSeatInEventById: "seats_in_events/getSeatInEventById",
      deleteBooking: "bookings/deleteBooking",
    }),

    goBack() {
      this.$router.back();
    },

    goToBookings() {
      const eventUid = this.$route.params.uid;
      this.$router.push(`/admin/bookings/${eventUid}`);
    },

    async initializeSeatsInEvents() {
      this.overlay = true;
      const eventUid = this.$route.params.uid;
      await this.initSeatsInEvent({ venue_id: 1, event_uid: eventUid });
      this.overlay = false;
    },
    async deleteSeatBooking() {
      if (!this.seat().booking) return;           // safety
      const bookingId = this.seat().booking.booking_id;    // grab the booking ID

      this.overlay = true;                         // show loader
      try {
        await this.deleteBooking(bookingId);       // Vuex action
        // reload seats so the UI reflects the deletion
        await this.getSeatsInEvent(this.$route.params.uid);
      } catch (err) {
        console.error("Error deleting booking:", err);
      } finally {
        this.overlay = false;                      // hide loader
        this.closeEditDialog();                    // close the dialog
      }
    },

    async openEditDialog(seatInEvent) {
      this.overlay = true;
      await this.getSeatInEventById(seatInEvent.seat_in_event_id)
      this.editingSeatInEvent = seatInEvent;
      this.seatInEventForm = {
        status: seatInEvent.status,
        price: seatInEvent.price,
      };
      this.editDialog = true;
      this.overlay = false;
    },

    closeEditDialog() {
      this.editDialog = false;
      this.seatInEventForm = { status: "", price: null };
    },

    async saveSeatInEvent() {
      this.overlay = true;
      const formData = { ...this.seatInEventForm };
      formData.id = this.editingSeatInEvent.seat_in_event_id;
      await this.updateSeatInEvent(formData);
      await this.getSeatsInEvent(this.$route.params.uid);
      this.closeEditDialog();
      this.overlay = false;
    },

    async loadVenues() {
      await this.getVenues();
    },
  },

  async created() {
    const eventUid = this.$route.params.uid;
    this.overlay = true;
    await this.getSeatsInEvent(eventUid);
    await this.loadVenues();
    this.overlay = false;
  },

  mounted() {
    this.panzoomInstance = Panzoom(this.$refs.zoomContainer, {
      maxZoom: 3,
      minZoom: 0.5,
      smoothScroll: true,
      bounds: true,
      boundsPadding: 0.5,
    });
    this.$refs.zoomContainer.addEventListener('wheel', (event) => {
      event.preventDefault();
      this.panzoomInstance.zoomWithWheel(event);
    });
  },

  beforeDestroy() {
    if (this.panzoomInstance) this.panzoomInstance.destroy();
  },
};
</script>

<style scoped>
.seat-gap {
  width: 30px;
  height: 30px;
}

.zoom-window {
  width: 1200px;
  height: 1700px;
  overflow: hidden;
  border: 1px solid #ccc;
  margin: 20px auto;
  position: relative;
}

.pan-zoom-area {
  width: 1200px;
  height: 1700px;
}

.venue-layout {
  padding: 20px;
}

.section-container {
  margin-bottom: 30px;
  border: 1px solid #ccc;
  padding: 10px;
}

.row-container {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}

.row-label {
  width: 40px;
  text-align: right;
  margin-right: 10px;
  font-weight: bold;
}

.seats-row {
  display: flex;
}

.seat-circle-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 5px;
  cursor: pointer;
}

.seat-circle {
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border 0.2s;
  border: 1px solid transparent;
}

.seat-circle:hover {
  border: 1px solid #888;
}

.seat-number {
  font-size: 10px;
  white-space: nowrap;
}

.seat-price {
  font-size: 10px;
  margin-top: 2px;
}

.seat-available {
  background-color: #428af5;
  color: white;
}

.seat-paid {
  background-color: #4caf50;
  color: white;
}

.seat-held {
  background-color: red;
  color: white;
}

.seat-booked {
  background-color: orange;
  color: white;
}

.seat-unavailable {
  background-color: gray;
  color: white;
}
</style>