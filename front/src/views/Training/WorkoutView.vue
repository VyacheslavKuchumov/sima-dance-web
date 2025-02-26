<template>
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1100">
      <v-toolbar flat>
        <v-toolbar-title>Тренировки</v-toolbar-title>
        
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog">
        </v-btn>
      </v-toolbar>

      <v-container v-if="workouts() && workouts().length">
        <v-row
          v-for="item in workouts()"
          :key="item.workout_id"
          >
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6">
                {{ item.workout_name }}
              </v-card-title>

              <v-card-text>
                <v-row dense>
                  <v-col cols="12">
                    <div class="text-caption">Дата</div>
                    <div class="text-h6">
                      {{ isoToRussianDate(item.workout_date) }}
                    </div>
                  </v-col>
                </v-row>
              </v-card-text>

              <v-card-actions class="justify-end">
                <v-btn
                  icon="mdi-weight-lifter"
                  color="green-darken-1"
                  variant="text"
                  @click="seeExercises(item)"
                ></v-btn>
                <v-btn
                  icon="mdi-pencil"
                  color="blue-darken-1"
                  variant="text"
                  @click="openEditDialog(item)"
                ></v-btn>
                <v-btn
                  icon="mdi-delete"
                  color="red-darken-1"
                  variant="text"
                  @click="confirmDelete(item)"
                ></v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-alert v-else type="info" class="ma-4">
        Нет данных
      </v-alert>
    </v-card>
  
    <!-- Диалог создания/редактирования -->
    <v-dialog v-model="editDialog" max-width="450px">
      <v-card>
        <v-card-title class="text-h5">
          {{ editingWorkout ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="workoutForm" v-model="valid" @submit.prevent="saveWorkout">
            <v-text-field
              v-model="workoutForm.workout_name"
              label="Название"
              clearable
              :rules="[rules.required]"
            ></v-text-field>
            
            <v-text-field
                v-model="workoutForm.workout_date"
                label="Дата тренировки"
                prepend-icon="mdi-calendar"
                @click="dateDialog = true"
                readonly
                clearable
                :rules="[rules.required]"
              />
              <v-dialog v-model="dateDialog" max-width="400px">
                <v-card>
                  <v-date-picker v-model="datePickerDate" />
                  <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn text color="primary" @click="dateDialog = false"
                      >Закрыть</v-btn
                    >
                    <v-btn text color="primary" @click="updateDate"
                      >OK</v-btn
                    >
                  </v-card-actions>
                </v-card>
              </v-dialog>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog()">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveWorkout()">
            Сохранить
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <!-- Диалог подтверждения удаления -->
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить "{{ workoutToDelete?.workout_name }}"?
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeConfirmDialog()">Отмена</v-btn>
          <v-btn color="red" @click="deleteConfirmed()">Удалить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </template>
  
  <script>
  import { mapActions, mapState } from "vuex";
  
  export default {
    data() {
      return {
        dateDialog: false,
        datePickerDate: new Date().toISOString().substr(0, 10),
        search: "",
        confirmDeleteDialog: false,
        editDialog: false,
        workoutToDelete: null,
        editingWorkout: null,
        workoutForm: {
          workout_name: "",
          workout_date: "",
        },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
      };
    },
    computed: {
      headers() {
        return [
          { title: "Название", key: "workout_name" },
          
          { title: "Дата", key: "workout_date", value: item => `${this.isoToRussianDate(item.workout_date) }`,},
          { title: "", key: "action_see_exercises", sortable: false },
          { title: "", key: "action_edit", sortable: false },
          { title: "", key: "action_delete", sortable: false },
        ];
      },
    },
    methods: {
        ...mapActions({
            getWorkouts: "workouts/getWorkouts",
            createWorkout: "workouts/createWorkout",
            updateWorkout: "workouts/updateWorkout",
            deleteWorkout: "workouts/deleteWorkout",
        }),
    
        workouts() {
            return this.$store.state.workouts.data;
        },
  
        isoToRussianDate(isoDate) {
            // Check if the input is a valid ISO date
            if (!isoDate || typeof isoDate !== "string") {
                throw new Error("Invalid input. Please provide a valid ISO date string.");
            }

            // Split the ISO date string into parts
            const [year, month, day] = isoDate.split("-");
            
            // Validate the extracted values
            if (!year || !month || !day || isNaN(Date.parse(isoDate))) {
                throw new Error("Invalid ISO date format.");
            }

            // Return the date in Russian format
            return `${day}.${month}.${year}`;
        },
        
        updateDate() {
            const date = new Date(this.datePickerDate);
            date.setMinutes(date.getMinutes() - date.getTimezoneOffset());
            this.workoutForm.workout_date = this.isoToRussianDate(date.toISOString().split("T")[0]);
            this.dateDialog = false;
            },
        openCreateDialog() {
            this.editingWorkout = null;
            this.workoutForm = { workout_name: "", workout_date: "" };
            this.editDialog = true;
        },
        openEditDialog(item) {
            this.editingWorkout = item;
            this.workoutForm = { workout_name: item.workout_name, workout_date: this.isoToRussianDate(item.workout_date) };
            this.editDialog = true;
        },
        closeEditDialog() {
            this.editDialog = false;
            this.workoutForm = { workout_name: "", workout_date: "" };
        },
        async saveWorkout() {
            const workoutData = { ...this.workoutForm };
            if (this.editingWorkout) {
                workoutData.workout_id = this.editingWorkout.workout_id;
                await this.updateWorkout(workoutData);
                await this.getWorkouts();
            } else {
                await this.createWorkout(workoutData);
                await this.getWorkouts();
            }
            this.closeEditDialog();
        },
        confirmDelete(item) {
            this.workoutToDelete = item;
            this.confirmDeleteDialog = true;
        },
        closeConfirmDialog() {
            this.confirmDeleteDialog = false;
            this.workoutToDelete = null;
        },
        async deleteConfirmed() {
            if (this.workoutToDelete) {
            await this.deleteWorkout(this.workoutToDelete.workout_id);
            await this.getWorkouts();
            this.closeConfirmDialog();
            }
        },
        seeExercises(item) {
            this.$router.push(`/workout/${item.workout_id}`);
        },
    },
    async created() {
        await this.getWorkouts();
    },
  };
  </script>
  