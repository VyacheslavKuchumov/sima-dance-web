<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate />
  </v-overlay>

  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Выписка билетов
    </v-card-title>
  </v-card>

  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1200">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack" />
      <v-spacer />
      <v-btn icon="mdi-filter" color="primary" @click="searchDialog = !searchDialog" />
    </v-toolbar>

    <v-container v-if="mergedBookings && mergedBookings.length">
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

        <!-- Новые колонки мест -->
        <template v-slot:item.section="{ item }">{{ item.section }}</template>
        <template v-slot:item.row="{ item }">{{ item.row }}</template>
        <template v-slot:item.number="{ item }">{{ item.number }}</template>
        <template v-slot:item.price="{ item }">{{ item.price }} р</template>

        <template v-slot:item.info="{ item }">
          <v-btn size="small" color="purple" class="mr-2" @click="confirmToggleTicket(item)">
            <v-icon>mdi-ticket</v-icon>
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
      <v-card-text v-if="selectedTicket" align="center">
        <p>Секция: {{ selectedTicket.section }}</p>
        <p>Ряд: {{ selectedTicket.row }}</p>
        <p>Место: {{ selectedTicket.number }}</p>
        <p>Цена: {{ selectedTicket.price }} р</p>
        <p>ФИО родителя: {{ selectedTicket.user.name }}</p>
        <p>ФИО ребёнка: {{ selectedTicket.user.child_name }}</p>
        <v-btn width="130" color="purple" @click="confirmToggleTicket(selectedTicket)">
          Билет
        </v-btn>
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
      <v-card-title class="text-h5 text-wrap">Подтвердите изменение статуса билета</v-card-title>
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
        <!-- Новый мультивыбор групп -->
        <v-select
          v-model="filterGroups"
          :items="['1 группа', 
                     '2 группа', 
                     '3 группа',
                     '4 группа', 
                     '5 группа', 
                     '6 группа', 
                     '7 группа',
                     '8 группа', 
                     '9 группа', 
                     '10 группа',
                     'Соло, дуэты']"
          label="Фильтр по группе"
          multiple
          clearable
          prepend-icon="mdi-format-list-bulleted"
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
      confirmToggleDialog: false,

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
      ],

      filterName: "",
      filterTicketConfirmed: false,
      filterTicketUnconfirmed: true,
      filterGroups: [],

      bookingToDelete: null,
      bookingToToggleTicket: null,
      selectedTicket: null,
    };
  },
  computed: {
    // Объединяем бронирования и места
    mergedBookings() {
      return (this.bookings() || []).map(b => {
        const seat = this.seats().find(s => s.seat_in_event_id === b.seat_in_event_id) || {};
        return {
          ...b,
          section: seat.seat?.section,
          row: seat.seat?.row,
          number: seat.seat?.number,
          price: seat.price,
        };
      });
    },
    filteredBookings() {
      let list = [...this.mergedBookings];

      // Только оплаченные
      list = list.filter(b => b.paid);

      // Статус билета
      if (this.filterTicketConfirmed !== this.filterTicketUnconfirmed) {
        list = list.filter(b => this.filterTicketConfirmed ? b.ticket_confirmed : !b.ticket_confirmed);
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
      toggleTicketStatus: "bookings/toggleTicketStatus",
      getSeatsInEvent: "seats_in_events/getSeatsInEvent",
    }),

    goBack() {
      this.$router.back();
    },
    async openInfoDialog(item) {
      this.overlay = true;
      this.infoDialog = true;
      this.selectedTicket = item;
      if (!item.section) {
        await this.getSeatsInEvent(this.$route.params.event_uid);
      }
      this.overlay = false;
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
    confirmToggleTicket(item) {
      this.bookingToToggleTicket = item;
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
    await this.getSeatsInEvent(this.$route.params.event_uid);
    this.overlay = false;
  },
};
</script>
