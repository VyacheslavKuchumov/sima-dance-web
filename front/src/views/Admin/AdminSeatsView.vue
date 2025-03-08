<template>
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Список мест (админ)
    </v-card-title>
  </v-card>

  <!-- Main Card with Toolbar and Venue Layout -->
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1200">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
      <v-spacer></v-spacer>
      <!-- <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn> -->
    </v-toolbar>

    <v-container v-if="seats() && seats().length" class="venue-layout">
      <!-- Loop through each section -->
      <div v-for="(rows, section) in groupedSeats" :key="section" class="section-container">
        <h3>{{ section }}</h3>
        <!-- Loop through each row in the section in descending order -->
        <div v-for="rowNumber in sortedRowKeys(rows)" :key="rowNumber" class="row-container">
          <!-- Row label on the left -->
          <div class="row-label">{{ rowNumber }}</div>
          <!-- Seats in the current row -->
          <div class="seats-row">
            <div
              v-for="seat in rows[rowNumber]"
              :key="seat.seat_id"
              class="seat"
              :class="{
                'seat-available': seat.status === 'available',
                'seat-held': seat.status === 'held',
                'seat-booked': seat.status === 'booked',
                'seat-unavailable': seat.status === 'unavailable'
              }"
              @click="openEditDialog(seat)"
            >
              <v-icon small>mdi-seat</v-icon>
              <span class="seat-number">{{ seat.number }}</span>
            </div>
          </div>
        </div>
      </div>
    </v-container>

    <v-alert v-else type="info" class="ma-4">
      Нет данных
    </v-alert>
  </v-card>

  <!-- Dialog for Creating/Editing a Seat -->
  <v-dialog v-model="editDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5">
        {{ editingSeat ? "Редактировать место" : "Создать место" }}
      </v-card-title>
      <v-card-text>
        <v-form ref="seatForm" v-model="valid" @submit.prevent="saveSeat">
          <v-text-field
            v-model="seatForm.section"
            label="Секция"
            clearable
            disabled
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="seatForm.row"
            label="Ряд"
            clearable
            disabled
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="seatForm.number"
            label="Номер"
            clearable
            disabled
            :rules="[rules.required]"
          ></v-text-field>
          <!-- :items="['available', 'held', 'booked', 'unavailable']" -->
          <v-select
            v-if="editingSeat"
            v-model="seatForm.status"
            label="Статус"
            :items="['available', 'unavailable']"
            :rules="[rules.required]"
          ></v-select>
          <v-text-field
            v-model="seatForm.price"
            label="Цена"
            type="number"
            
            :rules="[rules.required]"
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="closeEditDialog">Отмена</v-btn>
        <v-btn color="primary" :disabled="!valid" @click="saveSeat">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Delete Confirmation Dialog -->
  <v-dialog v-model="confirmDeleteDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
      <v-card-text>
        Вы уверены, что хотите удалить место (Ряд: {{ seatToDelete?.row }}, Номер: {{ seatToDelete?.number }})?
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="closeConfirmDialog">Отмена</v-btn>
        <v-btn color="red" @click="deleteConfirmed">Удалить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
import { mapActions } from "vuex";

export default {
  data() {
    return {
      confirmDeleteDialog: false,
      editDialog: false,
      seatToDelete: null,
      editingSeat: null,
      seatForm: {
        section: "",
        row: "",
        number: "",
        status: "",
        price: null,
      },
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
    };
  },
  computed: {
    // Group seats by section and then by row
    groupedSeats() {
      const groups = {};
      this.seats().forEach((seat) => {
        if (!groups[seat.section]) {
          groups[seat.section] = {};
        }
        if (!groups[seat.section][seat.row]) {
          groups[seat.section][seat.row] = [];
        }
        groups[seat.section][seat.row].push(seat);
      });
      return groups;
    },
  },
  methods: {
    seats() {
      return this.$store.state.seats.data;
    },
    // Helper method to sort row keys in descending order
    sortedRowKeys(rows) {
      return Object.keys(rows).sort((a, b) => Number(b) - Number(a));
    },
    ...mapActions({
      getSeats: "seats/getSeats",
      createSeat: "seats/createSeat",
      updateSeat: "seats/updateSeat",
      deleteSeat: "seats/deleteSeat",
    }),
    goBack() {
      this.$router.go(-1);
    },
    openCreateDialog() {
      this.editingSeat = null;
      this.seatForm = { section: "", row: "", number: "", status: "", price: null };
      this.editDialog = true;
    },
    openEditDialog(seat) {
      this.editingSeat = seat;
      this.seatForm = {
        section: seat.section,
        row: seat.row,
        number: seat.number,
        status: seat.status,
        price: seat.price,
      };
      this.editDialog = true;
    },
    closeEditDialog() {
      this.editDialog = false;
      this.seatForm = { section: "", row: "", number: "", status: "", price: null };
    },
    async saveSeat() {
      const formData = { ...this.seatForm };
      if (this.editingSeat) {
        formData.id = this.editingSeat.seat_id;
        await this.updateSeat(formData);
      } else {
        await this.createSeat(formData);
      }
      await this.getSeats();
      this.closeEditDialog();
    },
    confirmDelete(seat) {
      this.seatToDelete = seat;
      this.confirmDeleteDialog = true;
    },
    closeConfirmDialog() {
      this.confirmDeleteDialog = false;
      this.seatToDelete = null;
    },
    async deleteConfirmed() {
      if (this.seatToDelete) {
        await this.deleteSeat(this.seatToDelete.seat_id);
        await this.getSeats();
        this.closeConfirmDialog();
      }
    },
  },
  async created() {
    await this.getSeats();
  },
};
</script>

<style scoped>
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

/* Individual seat styling */
.seat {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  margin-right: 5px;
  cursor: pointer;
  border: 1px solid transparent;
  transition: border 0.2s;
}

.seat:hover {
  border: 1px solid #888;
}

/* Seat number styling */
.seat-number {
  font-size: 10px;
  margin-left: 2px;
}

/* Optional: Color coding for seat status */
.seat-available {
  color: green;
}
.seat-held {
  color: orange;
}
.seat-booked {
  color: red;
}
.seat-unavailable {
  color: gray;
}
</style>
