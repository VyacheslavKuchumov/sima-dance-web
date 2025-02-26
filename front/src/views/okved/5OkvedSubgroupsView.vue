<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">ОКВЭД Секции > Классы > Подклассы > Группы > ПОДГРУППЫ</v-card-title>
    </v-card>
  
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
  
      <v-container v-if="okvedSubgroups()">
        <v-row v-for="subgroup in okvedSubgroups()" :key="subgroup.subgroup_id">
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6 text-wrap">
                {{ subgroup.code }} - {{ subgroup.name }}
              </v-card-title>
              <v-card-actions class="justify-end">
                <v-btn icon="mdi-page-next" color="green-darken-1" variant="text" @click="goToPage(subgroup)"></v-btn>
                <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(subgroup)"></v-btn>
                <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(subgroup)"></v-btn>
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
          {{ editingSubgroup ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="subgroupForm" v-model="valid" @submit.prevent="saveSubgroup">
            <v-text-field v-model="subgroupForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
            <v-text-field v-model="subgroupForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveSubgroup">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить "{{ subgroupToDelete?.code }} - {{ subgroupToDelete?.name }}"?</v-card-text>
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
        subgroupToDelete: null,
        editingSubgroup: null,
        subgroupForm: { code: "", name: "" },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        group_id: null,
      };
    },
    methods: {
      okvedSubgroups() {
        return this.$store.state.okved.data;
      },
      ...mapActions({
        getOkvedSubgroups: "okved/getOkvedSubgroups",
        createOkvedSubgroup: "okved/createOkvedSubgroup",
        updateOkvedSubgroup: "okved/updateOkvedSubgroup",
        deleteOkvedSubgroup: "okved/deleteOkvedSubgroup",
      }),
      goToPage(subgroup) {
        this.$router.push({ name: "okved-activities", params: { id: subgroup.subgroup_id } });
      },
      goBack() {
        this.$router.go(-1);
      },
      openCreateDialog() {
        this.editingSubgroup = null;
        this.subgroupForm = { code: "", name: "" };
        this.editDialog = true;
      },
      openEditDialog(subgroup) {
        this.editingSubgroup = subgroup;
        this.subgroupForm = subgroup;
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.subgroupForm = { code: "", name: "" };
      },
      async saveSubgroup() {
        const subgroupData = { group_id: this.group_id, ...this.subgroupForm };
        if (this.editingSubgroup) {
          subgroupData.subgroup_id = this.editingSubgroup.subgroup_id;
          await this.updateOkvedSubgroup(subgroupData);
        } else {
          await this.createOkvedSubgroup(subgroupData);
        }
        await this.getOkvedSubgroups(this.group_id);
        this.closeEditDialog();
      },
      confirmDelete(subgroup) {
        this.subgroupToDelete = subgroup;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.subgroupToDelete = null;
      },
      async deleteConfirmed() {
        if (this.subgroupToDelete) {
          await this.deleteOkvedSubgroup(this.subgroupToDelete.id);
          await this.getOkvedSubgroups(this.group_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      const route = useRoute();
      const id = route.params.id;
      this.group_id = id;
      await this.getOkvedSubgroups(id);
    },
  };
  </script>
  