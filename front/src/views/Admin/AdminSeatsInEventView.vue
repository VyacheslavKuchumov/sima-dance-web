<template>
  <v-overlay :model-value="overlay" class="align-center justify-center">
    <v-progress-circular color="primary" size="64" indeterminate></v-progress-circular>
  </v-overlay>
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Настройка посадки
    </v-card-title>
  </v-card>
  
  <!-- Main Card with Toolbar -->
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
    </v-toolbar>
    <v-card max-height="600">
      <!-- Zoomable Container -->
      <div class="zoom-window" ref="zoomContainer">
        <div class="pan-zoom-area">
          <v-container v-if="seats_in_events() && seats_in_events().length" class="venue-layout">
            <!-- Venue plan content: Sections, rows, and seats -->
            <div v-for="(rows, section) in groupedSeats" :key="section" class="section-container">
              <h3>{{ section }}</h3>
              <div v-for="rowNumber in sortedRowKeys(rows)" :key="rowNumber" class="row-container">
                <div class="row-label">{{ rowNumber }}</div>
                <div class="seats-row">
                  <!-- Здесь кнопки заменены на круги -->
                  <div
                    v-for="seat in rows[rowNumber]"
                    :key="seat.seat_id"
                    class="seat-circle-wrapper"
                  >
                    <div
                      class="seat-circle"
                      :class="{
                        'seat-available': seat.status === 'available',
                        'seat-held': seat.status === 'held',
                        'seat-booked': seat.status === 'booked',
                        'seat-unavailable': seat.status === 'unavailable'
                      }"
                      @click="openEditDialog(seat)"
                    >
                      <span class="seat-number">{{ seat.seat.number }}</span>
                    </div>
                    <div class="seat-price">{{ seat.price }}р</div>
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
        {{ "Редактировать место" }}
      </v-card-title>
      <v-card-text>
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
import panzoom from 'panzoom'; // Install via npm: npm install panzoom

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
    // Group seats by section and then by row
    groupedSeats() {
      const groups = {};
      this.seats_in_events().forEach((seatInEvent) => {
        if (!groups[seatInEvent.seat.section]) {
          groups[seatInEvent.seat.section] = {};
        }
        if (!groups[seatInEvent.seat.section][seatInEvent.seat.row]) {
          groups[seatInEvent.seat.section][seatInEvent.seat.row] = [];
        }
        groups[seatInEvent.seat.section][seatInEvent.seat.row].push(seatInEvent);
      });
      console.log(groups);
      return groups;
    },
  },
  methods: {
    seats_in_events() {
      return this.$store.state.seats_in_events.data || [];
    },
    // Helper method to sort row keys in descending order
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
    }),
    goBack() {
      this.$router.go(-1);
    },
    async initializeSeatsInEvents() {
      this.overlay = true;
      console.log("initializing seats in events");
      const eventUid = this.$route.params.uid;
      await this.initSeatsInEvent({venue_id: 1, event_uid: eventUid});
      console.log("seats in events initialized");
      this.overlay = false;
    },
    openEditDialog(seatInEvent) {
      this.editingSeatInEvent = seatInEvent;
      this.seatInEventForm = {
        status: seatInEvent.status,
        price: seatInEvent.price,
      };
      this.editDialog = true;
    },
    closeEditDialog() {
      this.editDialog = false;
      this.seatInEventForm = { status: "", price: null };
    },
    async saveSeatInEvent() {
      this.overlay = true;
      const formData = { ...this.seatInEventForm };
      if (this.editingSeatInEvent) {
        formData.id = this.editingSeatInEvent.seat_in_event_id;
        await this.updateSeatInEvent(formData);
      } else {
        await this.createSeatInEvent(formData);
      }
      await this.getSeatsInEvent(this.$route.params.uid);
      this.closeEditDialog();
      this.overlay = false;
    },
    async loadVenues() {
      await this.getVenues();
      this.venues = this.$store.state.venues.data;
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
    // Initialize panzoom on the zoom container for panning and zooming
    this.panzoomInstance = panzoom(this.$refs.zoomContainer, {
      maxZoom: 3,
      minZoom: 0.5,
      smoothScroll: true,
      bounds: true,
      boundsPadding: 0.5,
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
  width: 1900px;      /* Visible window width */
  height: 2100px;     /* Visible window height */
  overflow: hidden;
  border: 1px solid #ccc;
  margin: 20px auto;
  position: relative;
}

.pan-zoom-area {
  width: 1800px;
  height: 2100px;
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
  cursor: pointer;
}

/* Стили для круга, отображающего место */
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

/* Стили для номера места внутри круга */
.seat-number {
  font-size: 10px;
  white-space: nowrap;
}

/* Цена под кругом */
.seat-price {
  font-size: 10px;
  margin-top: 2px;
}

/* Цветовое кодирование статуса места */
/* Доступное (синий) */
.seat-available {
  background-color: #428af5;
  color: white;
}

/* Занято (оранжевый) */
.seat-held {
  background-color: orange;
  color: white;
}

/* Бронировано (красный) */
.seat-booked {
  background-color: red;
  color: white;
}

/* Недоступно (серый) */
.seat-unavailable {
  background-color: gray;
  color: white;
}
</style>
