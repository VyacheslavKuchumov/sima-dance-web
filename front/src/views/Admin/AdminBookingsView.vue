<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate />
  </v-overlay>

  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Список бронирований
    </v-card-title>
  </v-card>

  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1200">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack" />
      <v-spacer />
      <v-btn icon="mdi-filter" color="primary" @click="searchDialog = !searchDialog" />
      <v-btn icon="mdi-seat" color="secondary" @click="goToSeats" />
      <v-btn icon="mdi-ticket" color="blue" @click="goToTickets" />
    </v-toolbar>

    <v-container v-if="mergedBookings && mergedBookings.length">
      <v-data-table
        :headers="headers"
        :items="filteredBookings"
        :items-per-page="-1"
        hide-default-footer
      >
        <template v-slot:item.status="{ item }">
          <v-icon v-if="item.confirmed && item.paid" color="green">mdi-check-circle</v-icon>
          <v-icon v-else-if="item.confirmed && !item.paid" color="orange">mdi-clock-outline</v-icon>
          <v-icon v-else color="red">mdi-close-circle</v-icon>
        </template>

        <template v-slot:item.info="{ item }">
          <v-btn size="small" color="primary" class="mr-2" @click="openInfoDialog(item)">
            <v-icon>mdi-information-slab-circle-outline</v-icon>
          </v-btn>
        </template>

        <template v-slot:item.payment="{ item }">
          <v-btn :disabled="!item.confirmed" size="small" color="green" class="mr-2" @click="confirmTogglePaid(item)">
            <v-icon>mdi-cash</v-icon>
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
      <v-card-text v-if="selectedBooking">
        <p>Секция: {{ selectedBooking.section }}</p>
        <p>Ряд: {{ selectedBooking.row }}</p>
        <p>Место: {{ selectedBooking.number }}</p>
        <p>Цена: {{ selectedBooking.price }} р</p>
        <p>ФИО родителя: {{ selectedBooking.user.name }}</p>
        <p>ФИО ребёнка: {{ selectedBooking.user.child_name }}</p>
      </v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn color="primary" @click="infoDialog = false">Ок</v-btn>
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

  <!-- Подтверждение оплаты -->
  <v-dialog v-model="confirmPaymentDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5 text-wrap">Подтвердите изменение статуса оплаты</v-card-title>
      <v-card-text>Вы уверены, что хотите изменить статус оплаты?</v-card-text>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="closePaymentDialog">Отмена</v-btn>
        <v-btn color="primary" @click="togglePaymentConfirmed">Подтвердить</v-btn>
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
          v-model="filterPaid"
          color="green"
          label="Только оплаченные"
          :disabled="filterUnconfirmed"
        />
        <v-switch
          v-model="filterUnpaid"
          color="orange"
          label="Только неоплаченные"
          :disabled="filterUnconfirmed"
        />
        <v-switch
          v-model="filterUnconfirmed"
          color="red"
          label="Не подтверждённые"
        />
        <!-- Добавленный мультивыбор групп -->
        <v-select
          v-model="filterGroups"
          :items="[
            'Беби 1', 'Беби 2', 'Средние 1', 'Средние 2', 'Средние 3',
            'Старшие 1', 'Старшие 2', 'Старшие 3', 'Cтаршие 11', 'Сборные'
          ]"
          label="Фильтр по группе"
          multiple
          clearable
          prepend-icon="mdi-format-list-bulleted"
          :disabled="filterUnconfirmed"
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

      headers: [
        { title: "Статус", key: "status" },
        { title: "Ребёнок", key: "user.child_name" },
        { title: "Родитель", key: "user.name" },
        { title: "Группа", key: "user.group_name" },
        { title: "Секция", key: "section" },
        { title: "Ряд", key: "row" },
        { title: "Место", key: "number" },
        { title: "Цена", key: "price" },
        { title: "", key: "info", sortable: false },
        { title: "", key: "payment", sortable: false },
      ],

      // Фильтры
      filterName: "",
      filterPaid: false,
      filterUnpaid: true,
      filterUnconfirmed: false,
      filterGroups: [],

      bookingToDelete: null,
      bookingToToggle: null,
      selectedBooking: null,
    };
  },
  computed: {
    // Объединяем бронирования и места
    mergedBookings() {
      return (this.bookings() || []).map(b => {
        const seatRecord = this.seats().find(s => s.seat_in_event_id === b.seat_in_event_id) || {};
        return {
          ...b,
          section: seatRecord.seat?.section,
          row: seatRecord.seat?.row,
          number: seatRecord.seat?.number,
          price: seatRecord.price,
        };
      });
    },
    filteredBookings() {
      let list = [...this.mergedBookings];

      // Исключаем подтверждённые тикеты
      list = list.filter(b => !b.ticket_confirmed);

      // Подтверждённость
      if (this.filterUnconfirmed) {
        list = list.filter(b => !b.confirmed);
      } else {
        list = list.filter(b => b.confirmed);
      }

      // Оплата
      if (this.filterPaid !== this.filterUnpaid) {
        list = list.filter(b => (this.filterPaid ? b.paid : !b.paid));
      }

      // ФИО ребёнка
      if (this.filterName) {
        const name = this.filterName.toLowerCase();
        list = list.filter(b => b.user.child_name.toLowerCase().includes(name));
      }

      // Группы
      if (this.filterGroups.length) {
        list = list.filter(b => this.filterGroups.includes(b.user.group_name));
      }

      return list;
    },
  },
  methods: {
    bookings() {
      return this.$store.state.bookings.data;
    },
    seats() {
      return this.$store.state.seats_in_events.data || [];
    },
    ...mapActions({
      getBookingsByEventUid: "bookings/getBookingsByEventUid",
      deleteBooking: "bookings/deleteBooking",
      togglePaidStatus: "bookings/togglePaidStatus",
      getSeatsInEvent: "seats_in_events/getSeatsInEvent",
    }),

    goBack() {
      this.$router.back();
    },
    goToSeats() {
      const eventUid = this.$route.params.event_uid;
      this.$router.push(`/admin/event/${eventUid}`);
    },
    goToTickets() {
      const eventUid = this.$route.params.event_uid;
      this.$router.push(`/admin/tickets/${eventUid}`);
    },
    async openInfoDialog(booking) {
      this.overlay = true;
      this.infoDialog = true;
      this.selectedBooking = booking;
      if (!booking.section) {
        // Если информация не загружена, можно загрузить по ID
        await this.getSeatsInEvent(this.$route.params.event_uid);
      }
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
      this.bookingToToggle = booking;
      this.confirmPaymentDialog = true;
    },
    closePaymentDialog() {
      this.confirmPaymentDialog = false;
      this.bookingToToggle = null;
    },
    async togglePaymentConfirmed() {
      if (this.bookingToToggle) {
        this.overlay = true;
        await this.togglePaidStatus(this.bookingToToggle.booking_id);
        await this.getBookingsByEventUid(this.$route.params.event_uid);
        this.overlay = false;
      }
      this.closePaymentDialog();
    },
  },
  async created() {
    this.overlay = true;
    await this.getBookingsByEventUid(this.$route.params.event_uid);
    await this.getSeatsInEvent(this.$route.params.event_uid);
    this.overlay = false;
  },
};
</script>
