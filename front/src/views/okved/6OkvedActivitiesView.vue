<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">ОКВЭД Секции > Классы > Подклассы > Группы > Подгруппы > ДЕЯТЕЛЬНОСТИ</v-card-title>
    </v-card>
  
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
  
      <v-container v-if="okvedActivities()">
        <v-row v-for="activity in okvedActivities()" :key="activity.activity_id">
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6 text-wrap">
                {{ activity.code }} - {{ activity.name }}
              </v-card-title>
              <v-card-actions class="justify-end">
                <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(activity)"></v-btn>
                <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(activity)"></v-btn>
              </v-card-actions>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
  
      <v-alert v-else type="info" class="ma-4">Нет данных</v-alert>
    </v-card>
  
    <v-dialog v-model="editDialog" max-width="450px">
      <v-card>
        <v-card-title class="text-h5">
          {{ editingActivity ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="activityForm" v-model="valid" @submit.prevent="saveActivity">
            <v-text-field v-model="activityForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
            <v-text-field v-model="activityForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveActivity">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить "{{ activityToDelete?.code }} - {{ activityToDelete?.name }}"?</v-card-text>
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
  import { useRoute } from "vue-router";
  
  export default {
    data() {
      return {
        confirmDeleteDialog: false,
        editDialog: false,
        activityToDelete: null,
        editingActivity: null,
        activityForm: { code: "", name: "" },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        subgroup_id: null,
      };
    },
    methods: {
      okvedActivities() {
        return this.$store.state.okved.data;
      },
      ...mapActions({
        getOkvedActivities: "okved/getOkvedActivities",
        createOkvedActivity: "okved/createOkvedActivity",
        updateOkvedActivity: "okved/updateOkvedActivity",
        deleteOkvedActivity: "okved/deleteOkvedActivity",
      }),
      goBack() {
        this.$router.go(-1);
      },
      openCreateDialog() {
        this.editingActivity = null;
        this.activityForm = { code: "", name: "" };
        this.editDialog = true;
      },
      openEditDialog(activity) {
        this.editingActivity = activity;
        this.activityForm = activity;
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.activityForm = { code: "", name: "" };
      },
      async saveActivity() {
        const activityData = { subgroup_id: this.subgroup_id, ...this.activityForm };
        if (this.editingActivity) {
          activityData.activity_id = this.editingActivity.activity_id;
          await this.updateOkvedActivity(activityData);
        } else {
          await this.createOkvedActivity(activityData);
        }
        await this.getOkvedActivities(this.subgroup_id);
        this.closeEditDialog();
      },
      confirmDelete(activity) {
        this.activityToDelete = activity;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.activityToDelete = null;
      },
      async deleteConfirmed() {
        if (this.activityToDelete) {
          await this.deleteOkvedActivity(this.activityToDelete.id);
          await this.getOkvedActivities(this.subgroup_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      const route = useRoute();
      const id = route.params.id;
      this.subgroup_id = id;
      await this.getOkvedActivities(id);
    },
  };
  </script>
  