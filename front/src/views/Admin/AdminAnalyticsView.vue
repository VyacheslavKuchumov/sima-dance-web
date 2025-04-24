<template>
    <v-overlay :model-value="overlay" class="align-center justify-center">
      <v-progress-circular color="primary" size="64" indeterminate />
    </v-overlay>
  
    <!-- Header -->
    <v-card max-width="800" class="elevation-0 mt-5 mx-auto">
      <v-card-title class="text-wrap" align="center">Аналитика концертов</v-card-title>
    </v-card>
  
    <!-- Total Registered Users -->
    <v-card max-width="600" class="elevation-2 mt-5 mx-auto pa-4">
      <v-row align="center">
        <v-col cols="12" class="text-center">
          <h2>Зарегистрировано пользователей всего:</h2>
          <h1>{{ totalUsers }}</h1>
        </v-col>
      </v-row>
    </v-card>
  
    <!-- Analytics by Event -->
    <v-card class="elevation-5 mt-5 mx-auto" max-width="600">
      <v-container>
        <v-row v-for="stat in eventAnalytics"
            :key="stat.eventUid"
            cols="12"
            sm="6">
          <v-col
            
          >
            <v-card class="ma-2 pa-4">
              <v-card-title class="text-wrap">{{ stat.eventName }}</v-card-title>
                <v-card-subtitle>{{ stat.eventDate }}</v-card-subtitle>
              <v-card-text>
                <div><strong>Забронировано мест:</strong> {{ stat.seatsCount }}</div>
                <div><strong>Выручка:</strong> {{ formatCurrency(stat.revenue) }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>
        <v-alert v-if="!eventAnalytics.length" type="info" class="ma-4">
          Нет данных аналитики
        </v-alert>
      </v-container>
    </v-card>
  </template>
  
  <script>
  import { mapActions, mapState } from "vuex";
  
  export default {
    data() {
      return {
        overlay: false,
        eventAnalytics: [],
      };
    },
    computed: {
      ...mapState({
        users: (state) => state.user.users || [],
      }),
      totalUsers() {
        return this.users.length;
      },
    },
    methods: {
      ...mapActions({
        getEvents: "events/getEvents",
        getSeatsInEvent: "seats_in_events/getSeatsInEvent",
        getAllUsers: "user/getAllUsers",
      }),
  
      // Загрузка и подсчет аналитики по концертам
      async loadAnalytics() {
        this.overlay = true;
        await this.getEvents();
        const events = this.$store.state.events.data || [];
  
        this.eventAnalytics = [];
        for (const ev of events) {
            await this.getSeatsInEvent(ev.event_uid);
            const seats = this.$store.state.seats_in_events.data || [];

            // 1. Фильтруем только забронированные места
            const bookedSeats = seats.filter(seat => seat.status === 'booked');

            // 2. Считаем их количество
            const seatsCount = bookedSeats.length;

            // 3. Считаем выручку только по этим местам
            const revenue = bookedSeats.reduce(
                (sum, seat) => sum + parseFloat(seat.price || 0),
                0
            );
          this.eventAnalytics.push({
            eventUid: ev.event_uid,
            eventName: ev.event_name,
            eventDate: ev.event_date,
            seatsCount,
            revenue,
          });
        }
  
        this.overlay = false;
      },
  
      // Форматируем число в рубли
      formatCurrency(amount) {
        return new Intl.NumberFormat("ru-RU", {
          style: "currency",
          currency: "RUB",
        }).format(amount);
      },
    },
    async created() {
      // Сначала загрузим пользователей, чтобы сразу показать число
      await this.getAllUsers();
      // Затем загрузим аналитику по событиям
      await this.loadAnalytics();
    },
  };
  </script>
  