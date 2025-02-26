<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title
        align="center">
        Профессии
      </v-card-title>
    
    </v-card>
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-btn icon="mdi-keyboard-backspace" color="primary" to="/"></v-btn>
        
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog">
        </v-btn>
      </v-toolbar>

      <v-container v-if="professions() && professions().length">
        <v-row
          v-for="item in professions()"
          :key="item.profession_id"
          >
          <v-col>
            <v-card class="ma-2">
              <v-card-title class="text-h6">
                {{ item.profession_name }}
              </v-card-title>

              <v-card-actions class="justify-end">
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
          {{ editingProfession ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="professionForm" v-model="valid" @submit.prevent="saveProfession">
            <v-text-field
              v-model="professionForm.profession_name"
              label="Название профессии"
              clearable
              :rules="[rules.required]"
            ></v-text-field>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog()">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveProfession()">
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
          Вы уверены, что хотите удалить "{{ professionToDelete?.profession_name }}"?
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
        confirmDeleteDialog: false,
        editDialog: false,
        professionToDelete: null,
        editingProfession: null,
        professionForm: {
          profession_name: "",
        },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
      };
    },
    methods: {
        ...mapActions({
            getProfessions: "professions/getProfessions",
            createProfession: "professions/createProfession",
            updateProfession: "professions/updateProfession",
            deleteProfession: "professions/deleteProfession",
        }),
    
        professions() {
            return this.$store.state.professions.data;
        },
        
        openCreateDialog() {
            this.editingProfession = null;
            this.professionForm = { profession_name: "" };
            this.editDialog = true;
        },
        openEditDialog(item) {
            this.editingProfession = item;
            this.professionForm = { profession_name: item.profession_name };
            this.editDialog = true;
        },
        closeEditDialog() {
            this.editDialog = false;
            this.professionForm = { profession_name: "" };
        },
        async saveProfession() {
            const professionData = { ...this.professionForm };
            if (this.editingProfession) {
                professionData.profession_id = this.editingProfession.profession_id;
                await this.updateProfession(professionData);
                await this.getProfessions();
            } else {
                await this.createProfession(professionData);
                await this.getProfessions();
            }
            this.closeEditDialog();
        },
        confirmDelete(item) {
            this.professionToDelete = item;
            this.confirmDeleteDialog = true;
        },
        closeConfirmDialog() {
            this.confirmDeleteDialog = false;
            this.professionToDelete = null;
        },
        async deleteConfirmed() {
            if (this.professionToDelete) {
            await this.deleteProfession(this.professionToDelete.profession_id);
            await this.getProfessions();
            this.closeConfirmDialog();
            }
        },
    },
    async created() {
        await this.getProfessions();
    },
  };
  </script>