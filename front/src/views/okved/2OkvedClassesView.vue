<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">ОКВЭД Секции > КЛАССЫ</v-card-title>
    </v-card>
    
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" @click="goBack"></v-btn>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
      
      <v-container v-if="okvedClasses()">
        <v-row v-for="okvedClass in okvedClasses()" :key="okvedClass.class_id">
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6 text-wrap">
                {{ okvedClass.code }} - {{ okvedClass.name }}
              </v-card-title>
              <v-card-actions class="justify-end">
                <v-btn icon="mdi-page-next" color="green-darken-1" variant="text" @click="goToPage(okvedClass)"></v-btn>
                <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(okvedClass)"></v-btn>
                <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(okvedClass)"></v-btn>
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
          {{ editingClass ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="classForm" v-model="valid" @submit.prevent="saveClass">
            <v-text-field v-model="classForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
            <v-text-field v-model="classForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveClass">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>Вы уверены, что хотите удалить "{{ classToDelete?.code }} - {{ classToDelete?.name }}"?</v-card-text>
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
        classToDelete: null,
        editingClass: null,
        classForm: { code: "", name: "" },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
        section_id: null,
      };
    },
    computed: {},
    methods: {
      okvedClasses() {
        return this.$store.state.okved.data;
      },
      ...mapActions({
        getOkvedClasses: "okved/getOkvedClasses",
        createOkvedClass: "okved/createOkvedClass",
        updateOkvedClass: "okved/updateOkvedClass",
        deleteOkvedClass: "okved/deleteOkvedClass",
      }),
  
      goToPage(okvedClass) {
        this.$router.push({ name: "okved-subclasses", params: { id: okvedClass.id } });
      },
        goBack() {
            this.$router.go(-1);
        },
      openCreateDialog() {
        this.editingClass = null;
        this.classForm = { code: "", name: "" };
        this.editDialog = true;
      },
      openEditDialog(okvedClass) {
        this.editingClass = okvedClass;
        this.classForm = okvedClass;
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.classForm = { code: "", name: "" };
      },
      async saveClass() {
        const classData = { section_id: this.section_id, ...this.classForm };
        if (this.editingClass) {
          classData.class_id = this.editingClass.class_id;
          await this.updateOkvedClass(classData);
        } else {
          await this.createOkvedClass(classData);
        }
        await this.getOkvedClasses(this.section_id);
        this.closeEditDialog();
      },
      confirmDelete(okvedClass) {
        this.classToDelete = okvedClass;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.classToDelete = null;
      },
      async deleteConfirmed() {
        if (this.classToDelete) {
          await this.deleteOkvedClass(this.classToDelete.id);
          await this.getOkvedClasses(this.section_id);
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
        const route = useRoute();
        const id = route.params.id;
        this.section_id = id;
        await this.getOkvedClasses(id);
    },
  };
  </script>
  