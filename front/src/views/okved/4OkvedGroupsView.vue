<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">ОКВЭД Секции > Классы > Подклассы > ГРУППЫ</v-card-title>
    </v-card>
  
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
  
      <v-container v-if="okvedGroups()">
        <v-row v-for="group in okvedGroups()" :key="group.group_id">
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6 text-wrap">
                {{ group.code }} - {{ group.name }}
              </v-card-title>
              <v-card-actions class="justify-end">
                <v-btn icon="mdi-page-next" color="green-darken-1" variant="text" @click="goToPage(group)"></v-btn>
                <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(group)"></v-btn>
                <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(group)"></v-btn>
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
          {{ editingGroup ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="groupForm" v-model="valid" @submit.prevent="saveGroup">
            <v-text-field v-model="groupForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
            <v-text-field v-model="groupForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveGroup">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить "{{ groupToDelete?.code }} - {{ groupToDelete?.name }}"?</v-card-text>
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
        groupToDelete: null,
        editingGroup: null,
        groupForm: { code: "", name: "" },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        subclass_id: null,
      };
    },
    methods: {
      okvedGroups() {
        return this.$store.state.okved.data;
      },
      ...mapActions({
        getOkvedGroups: "okved/getOkvedGroups",
        createOkvedGroup: "okved/createOkvedGroup",
        updateOkvedGroup: "okved/updateOkvedGroup",
        deleteOkvedGroup: "okved/deleteOkvedGroup",
      }),
      goToPage(group) {
        this.$router.push({ name: "okved-subgroups", params: { id: group.id } });
      },
      goBack() {
        this.$router.go(-1);
      },
      openCreateDialog() {
        this.editingGroup = null;
        this.groupForm = { code: "", name: "" };
        this.editDialog = true;
      },
      openEditDialog(group) {
        this.editingGroup = group;
        this.groupForm = group;
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.groupForm = { code: "", name: "" };
      },
      async saveGroup() {
        const groupData = { subclass_id: this.subclass_id, ...this.groupForm };
        if (this.editingGroup) {
          groupData.group_id = this.editingGroup.group_id;
          await this.updateOkvedGroup(groupData);
        } else {
          await this.createOkvedGroup(groupData);
        }
        await this.getOkvedGroups(this.subclass_id);
        this.closeEditDialog();
      },
      confirmDelete(group) {
        this.groupToDelete = group;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.groupToDelete = null;
      },
      async deleteConfirmed() {
        if (this.groupToDelete) {
          await this.deleteOkvedGroup(this.groupToDelete.id);
          await this.getOkvedGroups(this.subclass_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      const route = useRoute();
      const id = route.params.id;
      this.subclass_id = id;
      await this.getOkvedGroups(id);
    },
  };
  </script>
  