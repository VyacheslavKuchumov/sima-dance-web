<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">ОКВЭД Секции > Классы > ПОДКЛАССЫ</v-card-title>
    </v-card>
    
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
      
      <v-container v-if="okvedSubclasses()">
        <v-row v-for="subclass in okvedSubclasses()" :key="subclass.subclass_id">
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6 text-wrap">
                {{ subclass.code }} - {{ subclass.name }}
              </v-card-title>
              <v-card-actions class="justify-end">
                <v-btn icon="mdi-page-next" color="green-darken-1" variant="text" @click="goToPage(subclass)"></v-btn>
                <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(subclass)"></v-btn>
                <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(subclass)"></v-btn>
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
          {{ editingSubclass ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="subclassForm" v-model="valid" @submit.prevent="saveSubclass">
            <v-text-field v-model="subclassForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
            <v-text-field v-model="subclassForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveSubclass">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить "{{ subclassToDelete?.code }} - {{ subclassToDelete?.name }}"?</v-card-text>
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
        subclassToDelete: null,
        editingSubclass: null,
        subclassForm: { code: "", name: "" },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        class_id: null,
      };
    },
    methods: {
      okvedSubclasses() {
        return this.$store.state.okved.data;
      },
      ...mapActions({
        getOkvedSubclasses: "okved/getOkvedSubclasses",
        createOkvedSubclass: "okved/createOkvedSubclass",
        updateOkvedSubclass: "okved/updateOkvedSubclass",
        deleteOkvedSubclass: "okved/deleteOkvedSubclass",
      }),
      goToPage(okvedSubclass) {
        this.$router.push({ name: "okved-groups", params: { id: okvedSubclass.id } });
      },
      goBack() {
        this.$router.go(-1);
      },
      openCreateDialog() {
        this.editingSubclass = null;
        this.subclassForm = { code: "", name: "" };
        this.editDialog = true;
      },
      openEditDialog(subclass) {
        this.editingSubclass = subclass;
        this.subclassForm = subclass;
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.subclassForm = { code: "", name: "" };
      },
      async saveSubclass() {
        const subclassData = { class_id: this.class_id, ...this.subclassForm };
        if (this.editingSubclass) {
          subclassData.subclass_id = this.editingSubclass.subclass_id;
          await this.updateOkvedSubclass(subclassData);
        } else {
          await this.createOkvedSubclass(subclassData);
        }
        await this.getOkvedSubclasses(this.class_id);
        this.closeEditDialog();
      },
      confirmDelete(subclass) {
        this.subclassToDelete = subclass;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.subclassToDelete = null;
      },
      async deleteConfirmed() {
        if (this.subclassToDelete) {
          await this.deleteOkvedSubclass(this.subclassToDelete.id);
          await this.getOkvedSubclasses(this.class_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      const route = useRoute();
      const id = route.params.id;
      this.class_id = id;
      await this.getOkvedSubclasses(id);
    },
  };
  </script>
  