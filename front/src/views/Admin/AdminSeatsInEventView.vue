<template>
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Список мест (админ)
    </v-card-title>
  </v-card>

  <!-- Main Card with Toolbar -->
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1400">
    <v-toolbar flat>
      <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
      <v-spacer></v-spacer>
      <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
    </v-toolbar>
    <v-card class="ma-2" max-height="600">
      <!-- Zoomable Container -->
      <div class="zoom-window" ref="zoomContainer">
        <div class="pan-zoom-area">
          <v-container v-if="seats() && seats().length" class="venue-layout">
            <!-- Venue plan content: Sections, rows, and seats -->
            <div v-for="(rows, section) in groupedSeats" :key="section" class="section-container">
              <h3>{{ section }}</h3>
              <div v-for="rowNumber in sortedRowKeys(rows)" :key="rowNumber" class="row-container">
                <div class="row-label">{{ rowNumber }}</div>
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
        </div>
      </div>
    </v-card>
    
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
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="seatForm.row"
            label="Ряд"
            clearable
            :rules="[rules.required]"
          ></v-text-field>
          <v-text-field
            v-model="seatForm.number"
            label="Номер"
            clearable
            :rules="[rules.required]"
          ></v-text-field>
          <v-select
            v-if="editingSeat"
            v-model="seatForm.status"
            label="Статус"
            :items="['available', 'held', 'booked', 'unavailable']"
            :rules="[rules.required]"
          ></v-select>
          <v-text-field
            v-model="seatForm.price"
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
import panzoom from 'panzoom'; // Install via npm: npm install panzoom

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
      panzoomInstance: null,
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
  mounted() {
    // Initialize panzoom on the zoom container for panning and zooming
    this.panzoomInstance = panzoom(this.$refs.zoomContainer, {
      maxZoom: 3,
      minZoom: 0.5,
      smoothScroll: true,
    });
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
  width: 1400px;      /* Visible window width */
  height: 1600px;      /* Visible window height */
  overflow: hidden;
  border: 1px solid #ccc;
  margin: 20px auto;
  position: relative;
}

.pan-zoom-area {
  /* Overall dimensions of the venue plan */
  width: 1400px;
  height: 1600px;
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
