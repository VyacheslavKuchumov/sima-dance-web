<template>
    <v-overlay
      :model-value="overlay"
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        size="64"
        indeterminate
      ></v-progress-circular>
    </v-overlay>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">
        Список бронирований (админ)
      </v-card-title>
    </v-card>
  
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        
        <v-btn icon="mdi-filter" color="primary" @click="searchDialog = !searchDialog"></v-btn>
        
      </v-toolbar>
  
      <v-container v-if="bookings()">
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
          
          <template v-slot:item.payment="{ item }">
            <!-- Changed the click handler to open the confirmation dialog -->
            <v-btn :disabled="!item.confirmed" size="small" color="green" class="mr-2" @click="confirmTogglePaid(item)">
              <v-icon>mdi-cash</v-icon>
            </v-btn>
          </template>
          <template v-slot:item.delete="{ item }">
            <v-btn :disabled="item.confirmed" size="small" color="red" @click="confirmDelete(item)">
              <v-icon>mdi-delete</v-icon>
            </v-btn>
          </template>
        </v-data-table>
      </v-container>
  
      <v-alert v-else type="info" class="ma-4">
        Нет данных
      </v-alert>
    </v-card>
  
    <!-- Delete Confirmation Dialog -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить эту запись?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeConfirmDialog">Отмена</v-btn>
          <v-btn color="red" @click="deleteConfirmed">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <!-- Payment Toggle Confirmation Dialog -->
    <v-dialog v-model="confirmPaymentDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите изменение оплаты</v-card-title>
        <v-card-text>
          Вы уверены, что хотите изменить статус оплаты?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closePaymentDialog">Отмена</v-btn>
          <v-btn color="primary" @click="togglePaymentConfirmed">Подтвердить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="searchDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Поиск</v-card-title>
        <v-card-text>
          <!-- Filter Controls -->
          <v-text-field
            v-model="filterName"
            label="Фильтр по ФИО"
            clearable
            prepend-icon="mdi-account-search"
            :disabled="filterUnconfirmed"
          ></v-text-field>
          <v-switch
            v-model="filterUnpaid"
            color="primary"
            label="Только неоплаченные"
            :disabled="filterUnconfirmed"
          ></v-switch>
          <v-switch
            v-model="filterUnconfirmed"
            color="red"
            label="Не подтвержденные"
          ></v-switch>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
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
        search: false,
        headers: [
          { title: "Статус", key: "status" },
          { title: "Пользователь", key: "user.name" },
          { title: "", key: "payment", sortable: false },
          { title: "", key: "delete", sortable: false },
        ],
        confirmDeleteDialog: false,
        bookingToDelete: null,
        // New properties for payment confirmation
        confirmPaymentDialog: false,
        bookingToToggle: null,
        editDialog: false,
        bookingForm: {
          user_uid: "",
          seat_in_event_id: "",
          booking_date: "",
          confirmed: false,
          paid: false,
        },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        // Filter controls
        filterName: "",
        filterUnpaid: true,
        filterUnconfirmed: false,
      };
    },
    computed: {
      filteredBookings() {
        let filtered = this.bookings();
        filtered = filtered.filter(booking => booking.confirmed);
        
        // Filter by user's name if filterName is provided
        if (this.filterName) {
          filtered = filtered.filter(booking =>
            booking.user.name.toLowerCase().includes(this.filterName.toLowerCase())
          );
        }
        // If filterUnpaid is true, show only unpaid bookings
        if (this.filterUnpaid) {
          filtered = filtered.filter(booking => !booking.paid);
        }
        // If filterUnconfirmed is true, show only unconfirmed bookings
        if (this.filterUnconfirmed) {
          filtered = this.bookings().filter(booking => !booking.confirmed);
        }
        return filtered;
      },
    },
    methods: {
      bookings() {
        return this.$store.state.bookings.data;
      },
      ...mapActions({
        getBookingsByEventUid: "bookings/getBookingsByEventUid",
        createBooking: "bookings/createBooking",
        updateBooking: "bookings/updateBooking",
        deleteBooking: "bookings/deleteBooking",
        togglePaidStatus: "bookings/togglePaidStatus",
      }),
      goBack() {
        this.$router.go(-1);
      },
      // Existing method now called after confirmation
      async handleTogglePaidStatus(booking_id) {
        this.overlay = true;
        await this.togglePaidStatus(booking_id);
        await this.getBookingsByEventUid(this.$route.params.event_uid);
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
          this.closeConfirmDialog();
        }
        this.overlay = false;
      },
      // New method to open the payment confirmation dialog
      confirmTogglePaid(booking) {
        this.bookingToToggle = booking;
        this.confirmPaymentDialog = true;
      },
      // New method to close the payment confirmation dialog
      closePaymentDialog() {
        this.confirmPaymentDialog = false;
        this.bookingToToggle = null;
      },
      // New method to confirm payment toggle
      async togglePaymentConfirmed() {
        if (this.bookingToToggle) {
          await this.handleTogglePaidStatus(this.bookingToToggle.booking_id);
        }
        this.closePaymentDialog();
      },
    },
    async created() {
      this.overlay = true;
      await this.getBookingsByEventUid(this.$route.params.event_uid);
      this.overlay = false;
    },
  };
  </script>
  