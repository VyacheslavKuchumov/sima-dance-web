<template>
  <v-container>
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-toolbar-title>Выберите место в зале</v-toolbar-title>
      </v-toolbar>

      <v-row>
        <v-col cols="12" md="6">
          <v-card-text>
            <v-row>
              <v-col
                v-for="(row, rowIndex) in seats"
                :key="rowIndex"
                cols="12"
                md="auto"
              >
                <div class="d-flex">
                  <v-btn
                    v-for="(seat, seatIndex) in row"
                    :key="seatIndex"
                    :color="seat.selected ? 'green' : (seat.occupied ? 'red' : 'grey')"
                    class="ma-2"
                    @click="selectSeat(rowIndex, seatIndex)"
                  >
                    {{ seat.label }}
                  </v-btn>
                </div>
              </v-col>
            </v-row>
          </v-card-text>
        </v-col>
      </v-row>

      <v-card-actions>
        <v-btn color="warning" @click="clearSelection">Очистить выбор</v-btn>
        <v-spacer></v-spacer>
        <v-btn color="primary" @click="confirmSelection">Подтвердить</v-btn>
      </v-card-actions>
    </v-card>

    <!-- Диалог для показа выбранного места -->
    <v-dialog v-model="dialog" max-width="400">
      <v-card>
        <v-card-title class="headline">Уведомление</v-card-title>
        <v-card-text>
          <div v-if="selectedSeat">
            Вы выбрали место: <strong>{{ selectedSeat }}</strong>
          </div>
          <div v-else>
            Место не выбрано.
          </div>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="dialog = false">Закрыть</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>

<script>
export default {
  data() {
    return {
      seats: [
        [
          { label: 'A1', selected: false, occupied: false },
          { label: 'A2', selected: false, occupied: false },
          { label: 'A3', selected: false, occupied: true },
        ],
        [
          { label: 'B1', selected: false, occupied: false },
          { label: 'B2', selected: false, occupied: true },
          { label: 'B3', selected: false, occupied: false },
        ],
        // Дополнительные ряды можно добавить по необходимости
      ],
      dialog: false,
    };
  },
  computed: {
    selectedSeat() {
      // Поиск выбранного места
      for (let row of this.seats) {
        for (let seat of row) {
          if (seat.selected) return seat.label;
        }
      }
      return null;
    },
  },
  methods: {
    selectSeat(rowIndex, seatIndex) {
      // Если место занято, не реагировать на выбор
      if (this.seats[rowIndex][seatIndex].occupied) return;

      // Сбросить выбор всех мест (если требуется выбирать только одно место)
      this.seats.forEach(row => {
        row.forEach(seat => (seat.selected = false));
      });

      // Отметить выбранное место
      this.seats[rowIndex][seatIndex].selected = true;
    },
    clearSelection() {
      // Очистить выбор всех мест
      this.seats.forEach(row => {
        row.forEach(seat => (seat.selected = false));
      });
    },
    confirmSelection() {
      // Открыть диалоговое окно для подтверждения выбора
      this.dialog = true;
    },
  },
};
</script>

<style scoped>
/* Дополнительное оформление при необходимости */
</style>
