<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate />
  </v-overlay>

  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Выписка билетов
    </v-card-title>
  </v-card>

  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack" />
      <v-spacer />
      <v-btn icon="mdi-filter" color="primary" @click="searchDialog = !searchDialog" />
    </v-toolbar>

    <v-container v-if="bookings() && bookings().length">
      <v-data-table
        :headers="headers"
        :items="filteredBookings"
        :items-per-page="-1"
        hide-default-footer
      >
        <template v-slot:item.status="{ item }">
          <v-icon v-if="item.ticket_confirmed" color="green">mdi-check-circle</v-icon>
          <v-icon v-else color="orange">mdi-clock-outline</v-icon>

        </template>

        <template v-slot:item.user.child_name="{ item }">
          {{ item.user.child_name }}
        </template>

        <template v-slot:item.user.name="{ item }">
          {{ item.user.name }}
        </template>

        <template v-slot:item.info="{ item }">
          <v-btn size="small" color="primary" class="mr-2" @click="openInfoDialog(item)">
            <v-icon>mdi-information-slab-circle-outline</v-icon>
          </v-btn>
        </template>

        
      </v-data-table>
    </v-container>

    <v-alert v-else type="info" class="ma-4">
      Нет данных
    </v-alert>
  </v-card>

  <!-- Диалог информации -->
  <v-dialog v-model="infoDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5 text-wrap">
        Информация о бронировании
      </v-card-title>
      <v-card-text v-if="seat()" align="center">
        <p>Секция: {{ seat().seat?.section }}</p>
        <p>Место: {{ seat().seat?.number }}</p>
        <p>Ряд: {{ seat().seat?.row }}</p>
        <p>Цена: {{ seat().price }} р</p>
        <p>ФИО родителя: {{ seat().booking?.user.name }}</p>
        <p>ФИО ребёнка: {{ seat().booking?.user.child_name }}</p>
        
        <v-btn color="purple" @click="confirmToggleTicket(seat().booking)">Билет</v-btn>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="infoDialog = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Подтверждение удаления -->
  <v-dialog v-model="confirmDeleteDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
      <v-card-text>Вы уверены, что хотите удалить эту запись?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closeConfirmDialog">Отмена</v-btn>
        <v-btn color="red" @click="deleteConfirmed">Удалить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>



  <!-- Подтверждение статуса билета -->
  <v-dialog v-model="confirmToggleDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Подтвердите изменение статуса билета</v-card-title>
      <v-card-text>Вы уверены, что хотите изменить статус подтверждения билета?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closeToggleDialog">Отмена</v-btn>
        <v-btn color="primary" @click="toggleTicketConfirmed">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Диалог фильтров -->
  <v-dialog v-model="searchDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Поиск и фильтры</v-card-title>
      <v-card-text>
        <v-text-field
          v-model="filterName"
          label="Фильтр по ФИО ребёнка"
          clearable
          prepend-icon="mdi-account-search"
          :disabled="filterUnconfirmed"
        />
        <v-switch
          v-model="filterTicketConfirmed"
          color="green"
          label="Только выписанные"

        />
        <v-switch
          v-model="filterTicketUnconfirmed"
          color="orange"
          label="Только невыписанные"

        />

      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="searchDialog = false">Закрыть</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex";

export default {
  data() {
    return {
      overlay: false,
      searchDialog: false,
      infoDialog: false,
      confirmDeleteDialog: false,
      confirmPaymentDialog: false,
      confirmToggleDialog: false,

      headers: [
        { title: "Статус", key: "status" },
        { title: "Ребёнок", key: "user.child_name" },
        { title: "Родитель", key: "user.name" },
        { title: "", key: "info", sortable: false },

      ],

      // Фильтры
      filterName: "",
      filterTicketConfirmed: false,
      filterTicketUnconfirmed: true,

      bookingToDelete: null,
      bookingToTogglePayment: null,
      bookingToToggleTicket: null,
    };
  },
  computed: {
    filteredBookings() {
      let list = this.bookings() || [];

      // Фильтрация по статусу билета
      if (this.filterTicketConfirmed && !this.filterTicketUnconfirmed) {
        // Только подтверждённые
        list = list.filter(b => b.ticket_confirmed);
      } else if (this.filterTicketUnconfirmed && !this.filterTicketConfirmed) {
        // Только НЕподтверждённые
        list = list.filter(b => !b.ticket_confirmed);
      }
      // иначе (оба вкл. или оба выкл.) — без фильтра по статусу

      // Фильтрация по имени ребёнка
      if (this.filterName) {
        const name = this.filterName.toLowerCase();
        list = list.filter(b =>
          b.user.child_name.toLowerCase().includes(name)
        );
      }

      return list;
    },
  },
  methods: {
    bookings() {
      return this.$store.state.bookings.data;
    },
    seat() {
      return this.$store.state.seats_in_events.seat_in_event || null;
    },
    ...mapActions({
      getBookingsByEventUid: "bookings/getBookingsByEventUid",
      deleteBooking: "bookings/deleteBooking",
      togglePaidStatus: "bookings/togglePaidStatus",
      toggleTicketStatus: "bookings/toggleTicketStatus",
      getSeatInEventById: "seats_in_events/getSeatInEventById",
    }),

    goBack() {
      this.$router.back();
    },
    async openInfoDialog(booking) {
      this.overlay = true;
      this.infoDialog = true;
      await this.getSeatInEventById(booking.seat_in_event_id);
      this.overlay = false;
    },
    confirmDelete(booking) {
      this.bookingToDelete = booking;
      this.confirmDeleteDialog = true;
    },
    closeConfirmDialog() {
      this.confirmDeleteDialog = false;
      this.bookingToDelete = null;
    },
    async deleteConfirmed() {
      this.overlay = true;
      if (this.bookingToDelete) {
        await this.deleteBooking(this.bookingToDelete.booking_id);
        await this.getBookingsByEventUid(this.$route.params.event_uid);
      }
      this.closeConfirmDialog();
      this.overlay = false;
    },
    confirmTogglePaid(booking) {
      this.bookingToTogglePayment = booking;
      this.confirmPaymentDialog = true;
      
    },
    closePaymentDialog() {
      this.confirmPaymentDialog = false;
      this.bookingToTogglePayment = null;
    },
    async togglePaymentConfirmed() {
      if (this.bookingToTogglePayment) {
        this.overlay = true;
        await this.togglePaidStatus(this.bookingToTogglePayment.booking_id);
        await this.getBookingsByEventUid(this.$route.params.event_uid);
        
        this.overlay = false;
      }
      this.closePaymentDialog();
    },
    confirmToggleTicket(booking) {
      this.bookingToToggleTicket = booking;
      this.confirmToggleDialog = true;
    },
    closeToggleDialog() {
      this.confirmToggleDialog = false;
      
      this.bookingToToggleTicket = null;
    },
    async toggleTicketConfirmed() {
      if (this.bookingToToggleTicket) {
        this.overlay = true;
        await this.toggleTicketStatus(this.bookingToToggleTicket.booking_id);
        await this.getBookingsByEventUid(this.$route.params.event_uid);
        this.infoDialog = false;
        this.overlay = false;
      }
      this.closeToggleDialog();
    },
  },
  async created() {
    this.overlay = true;
    await this.getBookingsByEventUid(this.$route.params.event_uid);
    this.overlay = false;
  },
};
</script>
