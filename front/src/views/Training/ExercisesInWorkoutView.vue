<template>
    
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="1100">
    <v-toolbar flat>
      <v-toolbar-title>Упражнения в тренировке</v-toolbar-title>
      
      <v-spacer></v-spacer>
      <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog">
      </v-btn>
    </v-toolbar>

    <v-container v-if="exercisesInWorkout() && exercisesInWorkout().length">
      <v-row v-for="item in exercisesInWorkout()"
      :key="item.exercise_in_workout_id">
        <v-col>
          <v-card class="ma-2">
            <v-card-title class="text-h6">
              {{ item.exercise.exercise_name }}
            </v-card-title>

            <v-card-text>
              <v-row dense>
                <v-col cols="6">
                  <div class="text-caption">Вес</div>
                  <div class="text-h6">{{ item.weight }}</div>
                </v-col>
                <v-col cols="6">
                  <div class="text-caption">Повторения</div>
                  <div class="text-h6">{{ item.reps }}</div>
                </v-col>
                <v-col cols="12">
                  <div class="text-caption">Подход</div>
                  <div class="text-h6">{{ item.set }}</div>
                </v-col>
              </v-row>
            </v-card-text>

            <v-card-actions class="justify-end">
              <v-btn
                icon="mdi-plus"
                color="green"
                variant="text"
                @click="openQuickAddDialog(item)"
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

    <v-alert
      v-else
      type="info"
      class="ma-4"
    >
      Нет данных
    </v-alert>
  
      <!-- Create/Edit Dialog -->
      <v-dialog v-model="editDialog" max-width="450px">
        <v-card>
          
          <v-card-title class="text-h5">
            {{ editingEntry ? "Редактировать" : "Создать" }}
          </v-card-title>
          <v-card-text>
            <v-form ref="exerciseInWorkoutForm" v-model="valid" @submit.prevent="saveEntry">
              <v-select
                v-model="selectExercise"
                :items="exercises()"
                item-title="exercise_name"
                item-value="exercise_id"
                label="Упражнение"
                persistent-hint
                return-object

                :rules="[rules.required]"
              ></v-select>
              <v-text-field
                v-model="form.weight"
                label="Вес"
                type="number"
                :rules="[rules.isNumber]"
              ></v-text-field>
              <v-text-field
                v-model="form.reps"
                label="Повторения"
                type="number"
                :rules="[rules.isNumber]"
              ></v-text-field>
              <v-text-field
                v-model="form.set"
                label="Подход"
                type="number"
                :rules="[rules.isNumber]"
              ></v-text-field>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closeEditDialog()">Отмена</v-btn>
            <v-btn color="primary" :disabled="!valid" @click="saveEntry()">
              Сохранить
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Confirm Delete Dialog -->
      <v-dialog v-model="confirmDeleteDialog" max-width="400px">
        <v-card>
          <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
          <v-card-text>
            Вы уверены, что хотите удалить это упражнение из тренировки?
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="closeConfirmDialog()">Отмена</v-btn>
            <v-btn color="red" @click="deleteConfirmed()">Удалить</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </template>
  
  <script>
  import { mapActions, mapState } from "vuex";
  import { useRoute } from "vue-router";
import exercises from "@/store/exercises";
  
  export default {
    data() {
      return {
        workout_id: null,
        confirmDeleteDialog: false,
        editDialog: false,
        entryToDelete: null,
        editingEntry: null,
        selectExercise: null,
        form: {
          exercise_id: null,
          weight: null,
          reps: null,
          set: null,
        },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
          isNumber: value =>
          !isNaN(parseFloat(value)) && isFinite(value) || 'Только числа',
        },
      };
    },
    computed: {
    
      headers() {
        return [
          { title: "Упражнение", key: "exercise.exercise_name", sortable: false },
          { title: "Вес", key: "weight" },
          { title: "Повторения", key: "reps" },
          { title: "Подход", key: "set" },
          {title: "", key: "action_quick_add", sortable: false},
          { title: "", key: "action_edit", sortable: false },
          { title: "", key: "action_delete", sortable: false },
        ];
      },
      
    },
    methods: {
      exercisesInWorkout() {
        return this.$store.state.exercises_in_workout.data;
      },
      exercises() {
        return this.$store.state.exercises.data;
      },
      ...mapActions({
        getEntries: "exercises_in_workout/getExercisesInWorkout",
        createEntry: "exercises_in_workout/createExerciseInWorkout",
        updateEntry: "exercises_in_workout/updateExerciseInWorkout",
        deleteEntry: "exercises_in_workout/deleteExerciseInWorkout",
        getExercises: "exercises/getExercises",
      }),
      openQuickAddDialog(item){
        this.editingEntry = null;
        this.selectExercise = item.exercise;
        this.editDialog = true;
        this.form = item;
        this.form.set +=1;
      },
      openCreateDialog() {
        this.editingEntry = null;
        this.selectExercise = null;
        this.form = { exercise_id: null, weight: null, reps: null, set: null };
        this.editDialog = true;
      },
      openEditDialog(item) {
        this.selectExercise = item.exercise;
        this.editingEntry = item;
        this.form = { ...item };
        
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.selectExercise = null;
        this.form = { exercise_id: null, weight: null, reps: null, set: null };
      },
      async saveEntry() {
        const entryData = { ...this.form };
        if (this.editingEntry) {
          
          entryData.workout_id = this.workout_id;
          entryData.exercise_id = this.selectExercise.exercise_id;
          console.log(entryData);
          this.closeEditDialog();
          await this.updateEntry(entryData);
          
        } else {
          
          entryData.workout_id = this.workout_id;
          entryData.exercise_id = this.selectExercise.exercise_id;
          this.closeEditDialog();
          await this.createEntry(entryData);
          
          
        }
        await this.getEntries(this.workout_id);
        
      },
      confirmDelete(item) {
        this.entryToDelete = item;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.entryToDelete = null;
      },
      async deleteConfirmed() {
        if (this.entryToDelete) {
          await this.deleteEntry(this.entryToDelete.exercise_in_workout_id);
          await this.getEntries(this.workout_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      const route = useRoute();
      const workout_id = route.params.id;
      this.workout_id = workout_id;

      await this.getEntries(workout_id);
      await this.getExercises();
    },
  };
  </script>
  