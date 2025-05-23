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
  <!-- Header Card -->
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">
      Архив концертов
    </v-card-title>
  </v-card>

  <!-- Main Card with Toolbar and Cards for each Event -->
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
    <v-toolbar flat>
      <!-- <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn> -->
      <v-spacer></v-spacer>
      <!-- <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn> -->
    </v-toolbar>

    <v-container v-if="events() && events().length">
      <v-row 
        v-for="item in events()"
        :key="item.event_id"
      >
        <v-col>
          <v-card class="ma-2" >
            <!-- Event Image with Title Overlay -->
            <v-img :src="item.img_url" min-height="150px"  class="white--text align-end">
              
            </v-img>
            <v-card-title class="text-wrap">{{ item.event_name }}</v-card-title>
            <v-card-subtitle class="text-wrap">Архив</v-card-subtitle>
            <!-- Event Details -->
            <v-card-text>
              <div>
                <strong>Дата:</strong>
                {{ isoToRussianDate(item.event_date) }}
              </div>
            </v-card-text>

            <!-- Action Buttons -->
            <v-card-actions class="justify-end">
              <v-btn small color="green" @click="goToAdminEventBookings(item)">
                <v-icon>mdi-account-multiple</v-icon>
              </v-btn>
              <v-btn small color="secondary" @click="goToAdminEventSeats(item)">
                <v-icon>mdi-seat</v-icon>
              </v-btn>
              <v-btn small color="primary" @click="openEditDialog(item)">
                <v-icon>mdi-pencil</v-icon>
              </v-btn>
              <v-btn small color="red" @click="confirmDelete(item)">
                <v-icon>mdi-delete</v-icon>
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- No Data Alert -->
    <v-alert v-else type="info" class="ma-4">
      Нет данных
    </v-alert>
  </v-card>

  <!-- Dialog for Creating/Editing an Event -->
  <v-dialog v-model="editDialog" max-width="450px">
    <v-card>
      <v-card-title class="text-h5">
        {{ editingEvent ? "Редактировать" : "Создать" }}
      </v-card-title>
      <v-card-text>
        <v-form ref="eventForm" v-model="valid" @submit.prevent="saveEvent">
          <v-text-field
            v-model="eventForm.event_name"
            label="Название"
            clearable
            :rules="[rules.required]"
          ></v-text-field>

          <v-text-field
            v-model="eventForm.event_date"
            label="Дата события"
            prepend-icon="mdi-calendar"
            @click="openDateDialog"
            readonly
            clearable
            :rules="[rules.required]"
          ></v-text-field>

          <v-switch
            v-if="editingEvent"
            v-model="eventForm.archived"
            label="Архивировать"
            color="red-darken-1"
          ></v-switch>

          <v-text-field
            v-model="eventForm.img_url"
            label="URL изображения"
            clearable
          ></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="closeEditDialog">Отмена</v-btn>
        <v-btn color="primary" :disabled="!valid" @click="saveEvent">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Date Picker Dialog -->
  <v-dialog v-model="dateDialog" max-width="400px">
    <v-card>
      <v-date-picker v-model="datePickerDate" />
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text color="primary" @click="dateDialog = false">Закрыть</v-btn>
        <v-btn text color="primary" @click="updateDate">OK</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Delete Confirmation Dialog -->
  <v-dialog v-model="confirmDeleteDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
      <v-card-text>
        Вы уверены, что хотите удалить событие «{{ eventToDelete?.event_name }}»?
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
      overlay: false,
      dateDialog: false,
      datePickerDate: new Date().toISOString().substr(0, 10),
      confirmDeleteDialog: false,
      editDialog: false,
      eventToDelete: null,
      editingEvent: null,
      eventForm: {
        event_name: "",
        event_date: "",
        img_url: "",
        archived: false,
      },
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
    };
  },
  methods: {
    events() {
      return this.$store.state.events.data;
    },
    ...mapActions({
      getEvents: "events/getArchivedEvents",
      createEvent: "events/createEvent",
      updateEvent: "events/updateEvent",
      deleteEvent: "events/deleteEvent",
    }),
    goBack() {
      this.$router.go(-1);
    },
    goToAdminEventSeats(item) {
        this.$router.push(`/admin/event/${item.event_uid}`);
      },
    goToAdminEventBookings(item) {
      this.$router.push(`/admin/bookings/${item.event_uid}`);
    },
    isoToRussianDate(isoDate) {
      if (!isoDate || typeof isoDate !== "string") {
        throw new Error("Invalid input. Please provide a valid ISO date string.");
      }
      const [year, month, day] = isoDate.split("-");
      if (!year || !month || !day || isNaN(Date.parse(isoDate))) {
        throw new Error("Invalid ISO date format.");
      }
      return `${day}.${month}.${year}`;
    },
    russianDateToIso(russianDate) {
      if (!russianDate || typeof russianDate !== "string") {
        throw new Error("Invalid input. Please provide a valid Russian date string.");
      }
      const [day, month, year] = russianDate.split(".");
      if (!year || !month || !day || isNaN(Date.parse(`${year}-${month}-${day}`))) {
        throw new Error("Invalid Russian date format.");
      }
      return `${year}-${month}-${day}`;
    },
    updateDate() {
      const date = new Date(this.datePickerDate);
      date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
      this.eventForm.event_date = this.isoToRussianDate(date.toISOString().split("T")[0]);
      this.dateDialog = false;
    },
    openDateDialog() {
      this.datePickerDate = new Date().toISOString().substr(0, 10);
      this.dateDialog = true;
    },
    openCreateDialog() {
      this.editingEvent = null;
      this.eventForm = { event_name: "", event_date: "", img_url: "", archived: false };
      this.editDialog = true;
    },
    openEditDialog(event) {
      this.editingEvent = event;
      this.eventForm = {
        event_name: event.event_name,
        event_date: this.isoToRussianDate(event.event_date),
        img_url: event.img_url,
        archived: event.archived,
      };
      this.editDialog = true;
    },
    closeEditDialog() {
      this.editDialog = false;
      this.eventForm = { event_name: "", event_date: "", img_url: "", archived: false };
    },
    async saveEvent() {
      const formData = { ...this.eventForm };
      formData.event_date = this.russianDateToIso(formData.event_date);
      if (this.editingEvent) {
        this.overlay = true;
        formData.id = this.editingEvent.event_id;
        await this.updateEvent(formData);
        this.overlay = false;
      } else {
        this.overlay = true;
        // Remove archived property when creating a new event since it's not part of the creation schema.
        delete formData.archived;
        await this.createEvent(formData);
        this.overlay = false;
      }
      await this.getEvents();
      this.closeEditDialog();
    },
    confirmDelete(event) {
      this.eventToDelete = event;
      this.confirmDeleteDialog = true;
    },
    closeConfirmDialog() {
      this.confirmDeleteDialog = false;
      this.eventToDelete = null;
    },
    async deleteConfirmed() {
      if (this.eventToDelete) {
        this.overlay = true;
        await this.deleteEvent(this.eventToDelete.event_id);
        await this.getEvents();
        this.closeConfirmDialog();
        this.overlay = false;
      }
    },
  },
  async created() {
    this.overlay = true;
    await this.getEvents();
    this.overlay = false;
  },
};
</script>
