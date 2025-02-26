<template>
  <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
    <v-card-title class="text-wrap" align="center">ОКВЭД Разделы</v-card-title>
  </v-card>
  
  <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
    <v-toolbar flat>
      
      <v-spacer></v-spacer>
      <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
    </v-toolbar>
    
    <v-container v-if="okvedSections()">
      <v-row v-for="section in okvedSections()" :key="section.section_id">
        <v-col>
          <v-card class="ma-2">
            <v-card-title class="text-h6 text-wrap">
              {{ section.code }} - {{ section.name }}
            </v-card-title>
            <v-card-actions class="justify-end">
              <v-btn icon="mdi-page-next" color="green-darken-1" variant="text" disabled @click="goToPage(section)"></v-btn>
              <v-btn icon="mdi-pencil" color="blue-darken-1" variant="text" @click="openEditDialog(section)"></v-btn>
              <v-btn icon="mdi-delete" color="red-darken-1" variant="text" @click="confirmDelete(section)"></v-btn>
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
        {{ editingSection ? "Редактировать" : "Создать" }}
      </v-card-title>
      <v-card-text>
        <v-form ref="sectionForm" v-model="valid" @submit.prevent="saveSection">
          <v-text-field v-model="sectionForm.code" label="Код" clearable :rules="[rules.required]"></v-text-field>
          <v-text-field v-model="sectionForm.name" label="Наименование" clearable :rules="[rules.required]"></v-text-field>
        </v-form>
      </v-card-text>
      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="closeEditDialog">Отмена</v-btn>
        <v-btn color="primary" :disabled="!valid" @click="saveSection">Сохранить</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <v-dialog v-model="confirmDeleteDialog" max-width="400px">
    <v-card>
      <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
      <v-card-text>Вы уверены, что хотите удалить "{{ sectionToDelete?.code }} - {{ sectionToDelete?.name }}"?</v-card-text>
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
      confirmDeleteDialog: false,
      editDialog: false,
      sectionToDelete: null,
      editingSection: null,
      sectionForm: { code: "", name: "" },
      valid: false,
      rules: {
        required: (value) => !!value || "Это поле обязательно",
      },
    };
  },
  computed: {
    
  },
  methods: {
    okvedSections() {
      return this.$store.state.okved.data;
    },
    ...mapActions({
      getOkvedSections: "okved/getOkvedSections",
      createOkvedSection: "okved/createOkvedSection",
      updateOkvedSection: "okved/updateOkvedSection",
      deleteOkvedSection: "okved/deleteOkvedSection",
    }),

    goToPage(section) {
      this.$router.push({ name: "okved-classes", params: { id: section.id } });
    },

    openCreateDialog() {
      this.editingSection = null;
      this.sectionForm = { code: "", name: "" };
      this.editDialog = true;
    },
    openEditDialog(section) {
      this.editingSection = section;
      this.sectionForm = section;
      this.editDialog = true;
    },
    closeEditDialog() {
      this.editDialog = false;
      this.sectionForm = { code: "", name: "" };
    },
    async saveSection() {
      const sectionData = { ...this.sectionForm };
      if (this.editingSection) {
        sectionData.section_id = this.editingSection.section_id;
        await this.updateOkvedSection(sectionData);
      } else {
        await this.createOkvedSection(sectionData);
      }
      await this.getOkvedSections();
      this.closeEditDialog();
    },
    confirmDelete(section) {
      this.sectionToDelete = section;
      this.confirmDeleteDialog = true;
    },
    closeConfirmDialog() {
      this.confirmDeleteDialog = false;
      this.sectionToDelete = null;
    },
    async deleteConfirmed() {
      if (this.sectionToDelete) {
        await this.deleteOkvedSection(this.sectionToDelete.id);
        await this.getOkvedSections();
        this.closeConfirmDialog();
      }
    },
  },
  async created() {
    await this.getOkvedSections();
  },
};
</script>
