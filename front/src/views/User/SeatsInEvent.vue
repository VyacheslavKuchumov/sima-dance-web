<template>
  
  <v-snackbar
      v-model="snackbar"
      class="elevation-24"
      color="deep-purple-accent-4"
      :timeout="10000"
      vertical
    >
      
    <div class="text-subtitle-1 pb-2">Не забудьте оплатить места!</div>


    <template v-slot:actions>
      <v-btn color="white" variant="text" @click="paymentDialog = true; snackbar = false">
        ОПЛАТИТЬ
      </v-btn>
    </template>
    
  </v-snackbar>

  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Схема зала
    </v-card-title>
  </v-card>
  
  <!-- Main Card with Toolbar -->
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1400">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-cash-multiple" color="secondary" @click="paymentDialog=true; snackbar=false"></v-btn>
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
                  <!-- Здесь обрабатываем и реальные места, и пропуски -->
                  <div
                    v-for="(seat, index) in rows[rowNumber]"
                    :key="seat ? seat.seat_in_event_id : 'gap-' + index"
                    class="seat-circle-wrapper"
                  >
                    <template v-if="seat">
                      <div
                        class="seat-circle"
                        :class="{
                          'seat-available': seat.status === 'available',
                          'seat-held': seat.status === 'held',
                          'seat-booked': seat.status === 'booked' && !isCurrentUserSeat(seat),
                          'seat-booked-current': seat.status === 'booked' && isCurrentUserSeat(seat),
                          'seat-unavailable': seat.status === 'unavailable'
                        }"
                        @click="bookSeat(seat)"
                      >
                        <span class="seat-number">{{ seat.seat.number }}</span>
                      </div>
                      <div class="seat-price">{{ seat.price }}р</div>
                    </template>
                    <template v-else>
                      <!-- Элемент-пропуск -->
                      <div class="seat-gap"></div>
                    </template>
                  </div>
                </div>
              </div>
            </div>
          </v-container>
          <v-alert v-else type="info" class="ma-4">
            <p v-if="!overlay">Администратор не инициализировал места</p>
          </v-alert>
        </div>
      </div>
    </v-card>
  </v-card>

  <!-- Dialog for confirming booking -->
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
        <v-btn color="red" @click="cancelBooking">Отменить</v-btn>
        <v-btn color="primary" @click="saveBooking">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <!-- Dialog for showing booking info -->
  <v-dialog v-model="bookingInfoDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5 text-wrap">
        Информация о бронировании
      </v-card-title>
      <v-card-text>

        <p>Секция: {{ seat().seat.section }}</p>
        <p>Место: {{ seat().seat.number }}</p>
        <p>Ряд: {{ seat().seat.row }}</p>

        <p>Цена: {{ seat().price }}р</p>
        <p>ФИО: {{ seat().booking.user.name }}</p>

        <p v-if="seat().status == 'held'"><strong>Бронь не подтверждена!</strong></p>
        <v-btn
          v-if="seat().status === 'held'"
          class="ma-5"
          color="error"
          @click="confirmFunc(seat().booking.booking_id)"
        >
          Подтвердить бронь
        </v-btn>
        
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" @click="cancelBooking">Удалить бронь</v-btn>
        <v-btn color="primary" @click="bookingInfoDialog = false">Ок</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <!-- Dialog for showing error messages -->
  <v-dialog v-model="bookingErrorDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5 text-wrap">
        Ошибка
      </v-card-title>
      <v-card-text>
        <p>Место уже забронировано</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn color="red" @click="bookingErrorDialog = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
  <v-dialog v-model="paymentDialog" max-width="500px">
    <v-card>
      <v-card-title class="text-h5">Оплата брони</v-card-title>
      <v-card-text>
        <!-- LEGACY!!! -->
        <!-- QR-код для оплаты через Тинькофф -->
        <!-- <v-img
          src="@/assets/qr_code.jpg"
          alt="QR-код Тинькофф для оплаты"
          contain
          max-width="250"
          class="mx-auto mb-4"
        /> -->
        <p>
          Вы забронировали {{ bookedSeats().length }} мест
          на сумму <strong>{{ totalPrice() }} ₽</strong>.
        </p>
        
      </v-card-text>
      <v-card-actions>
        <v-btn primary to="https://payment.alfabank.ru/sc/TzMfqhRHpufumcmu">Оплатить</v-btn>
        <v-spacer />
        <v-btn text @click="paymentDialog = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

</template>

<script>
import { mapActions } from "vuex";
import Panzoom from '@panzoom/panzoom'
import WebSocketService from '@/websocket/WebSocketService.js';

export default {
  data() {
    return {
      paymentDialog: false,
      snackbar: false,
      wsService: null,
      overlay: false,
      bookingDialog: false,
      bookingInfoDialog: false,
      bookingErrorDialog: false,
      bookingData: null,
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
      panzoomInstance: null,
      phoneNumber: "+7 (950) 465-99-99",
    };
  },
  computed: {
    // Группируем места по секциям и рядам и добавляем пропуск для Балкона, 7 ряда
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
    user() {
      return this.$store.state.user.user;
    },
    seats_in_events() {
      return this.$store.state.seats_in_events.data || [];
    },

    seat(){
      return this.$store.state.seats_in_events.seat_in_event || null;
    },

    // Сортировка ключей рядов в обратном порядке (по номеру ряда)
    sortedRowKeys(rows) {
      return Object.keys(rows).sort((a, b) => Number(b) - Number(a));
    },
    // Проверка, принадлежит ли место текущему пользователю
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
      getSeatInEventById: "seats_in_events/getSeatInEventById",
      
      confirmBooking: "bookings/confirmBooking",
      createBooking: "bookings/createBooking",
      deleteBooking: "bookings/deleteBooking",
      
      getUser: "user/getUserByUid",
      updateSeatInStore: "seats_in_events/updateSeatInStore",
    }),
    goBack() {
      this.$router.go(-1);
    },
    bookedSeats() {
     return this.seats_in_events().filter(
       seat =>
        seat.booking &&
         seat.booking.user_uid === this.$store.state.user.user.user_uid
     );
   },
   // total price of those seats
   totalPrice() {
     return this.bookedSeats().reduce((sum, s) => sum + s.price, 0);
   },
   async confirmFunc(bookingId) {
      this.overlay = true;
      
      await this.confirmBooking(bookingId);
      await this.getSeatsInEvent(this.$route.params.uid);
      this.bookingInfoDialog = false;
    
      this.overlay = false;
      
    },
    async bookSeat(item) {
      this.overlay = true;
      console.log("Testing", item);
      await this.getSeatInEventById(item.seat_in_event_id);
      console.log(this.seat());
      this.overlay = false;

      try {
        if (this.seat().booking && this.seat().booking.user_uid === this.$store.state.user.user.user_uid) {
          this.bookingInfoDialog = true;
          return;
        }
        if (this.seat().status === "unavailable" || this.seat().status === "held" || this.seat().status === "booked") {
          this.bookingErrorDialog = true;
          return;
        }
        this.overlay = true;
        const data = {
          user_uid: this.$store.state.user.user.user_uid,
          seat_in_event_id: item.seat_in_event_id,
        };
        const bookingResponse = await this.createBooking(data);
        await this.getSeatInEventById(item.seat_in_event_id);
        
        const updatedSeat = this.seats_in_events().find(
          (seat) => seat.seat_in_event_id === item.seat_in_event_id
        );
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
        const bookingId = this.seat()?.booking?.booking_id;
        if (!bookingId) {
          throw new Error("Booking ID not found.");
        }
        await this.deleteBooking(bookingId);
        await this.getSeatsInEvent(this.$route.params.uid);
        this.bookingDialog = false;
        this.bookingInfoDialog = false;
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
        this.snackbar = true;
      }
    },
    async initWebSocket() {
      this.wsService = new WebSocketService();
      try {
        await this.wsService.connect();
        this.wsService.onMessage((raw_data) => {
          console.log("Message received:", raw_data);
          const payload = JSON.parse(raw_data);
          this.updateSeatInStore(payload.data);
        });
        this.wsService.onClose((event) => {
          console.log("WebSocket closed:", event);
        });
      } catch (error) {
        console.error("Failed to connect:", error);
      }
    }
  },
  async created() {
    const eventUid = this.$route.params.uid;
    this.overlay = true;
    await this.getSeatsInEvent(eventUid);
    this.uid = localStorage.getItem("uid");
    if (this.uid) {
      await this.getUser();
    }
    await this.initWebSocket();
    this.overlay = false;
  },
  async mounted() {
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
    if (this.panzoomInstance) {
      this.panzoomInstance.destroy();
    }
    if (this.wsService && typeof this.wsService.disconnect === 'function') {
      this.wsService.disconnect();
    }
  },
  beforeRouteLeave(to, from, next) {
    if (this.wsService && typeof this.wsService.disconnect === 'function') {
      this.wsService.disconnect();
    }
    if (this.panzoomInstance) {
      this.panzoomInstance.destroy();
    }
    next();
  },
};
</script>

<style scoped>
.zoom-window {
  width: 1200px;      /* Visible window width */
  height: 1700px;     /* Visible window height */
  overflow: hidden;
  border: 1px solid #ccc;
  margin: 20px auto;
  position: relative;
}

.pan-zoom-area {
  width: 1200px;
  height: 1700px;
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

/* Wrapper for each seat circle and price */
.seat-circle-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-right: 5px;
}

/* The seat circle styling */
.seat-circle {
  border-radius: 50%;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border 0.2s;
  border: 1px solid transparent;
  cursor: pointer;
}

.seat-circle:hover {
  border: 1px solid #2b2b2b;
}

/* Seat number styling inside the circle */
.seat-number {
  font-size: 10px;
  white-space: nowrap;
}

/* Price styling: beneath the circle */
.seat-price {
  font-size: 10px;
  margin-top: 2px;
}

/* Color coding for seat status */
/* Blue: Available Seats */
.seat-available {
  background-color: #428af5;
  color: white;
}

/* For seats held by others (if needed) */
.seat-held {
  background-color: orange;
  color: white;
}

/* Red: Other Users' Booked Seats */
.seat-booked {
  background-color: red;
  color: white;
}

/* Green: Current User's Booked Seats */
.seat-booked-current {
  background-color: green;
  color: white;
}

/* Gray: Unavailable Seats */
.seat-unavailable {
  background-color: red;
  color: white;
}

/* Стили для элемента-пропуска */
.seat-gap {
  width: 30px;
  height: 30px;
}
</style>
