<template>
    <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
      <v-card-title class="text-wrap" align="center">
        СРЕДНЕГОДОВАЯ ЧИСЛЕННОСТЬ ЗАНЯТЫХ ПО ВИДАМ ЭКОНОМИЧЕСКОЙ ДЕЯТЕЛЬНОСТИ
      </v-card-title>
    </v-card>
  
    <v-card class="elevation-5 mt-5 ml-auto mr-auto" max-width="800">
      <v-toolbar flat>
        <v-spacer></v-spacer>
        <v-btn icon="mdi-plus" color="primary" @click="openCreateDialog"></v-btn>
      </v-toolbar>
  
      <v-container v-if="employmentMinstat() && employmentMinstat().length">
        <v-data-table
          :headers="headers"
          :items="employmentMinstat()"
          :group-by="groupBy"
          :items-per-page="-1"
          hide-default-footer
          >

          <template
            v-slot:group-header="{ item, columns, toggleGroup, isGroupOpen }"
          >
            <tr>
              <td :colspan="columns.length" @click="toggleGroup(item)">
                <v-btn
                  :icon="
                    isGroupOpen(item) ? 'mdi-chevron-down' : 'mdi-chevron-right'
                  "
                  size="small"
                  variant="text"
                ></v-btn>
                <span>{{ item.value }}</span>
              </td>
            </tr>
          </template>

          <template v-slot:item.edit="{ item }">
            <v-btn size="small" color="primary" class="mr-2" @click="openEditDialog(item)"><v-icon>mdi-pencil</v-icon></v-btn>
            
          </template>
          <template v-slot:item.delete="{ item }">
            <v-btn size="small" color="red" @click="confirmDelete(item)"><v-icon>mdi-delete</v-icon></v-btn>
          </template>
          
        </v-data-table>
      </v-container>
  
      <v-alert v-else type="info" class="ma-4">
        Нет данных
      </v-alert>
    </v-card>
  
    <v-dialog v-model="editDialog" max-width="450px">
      <v-card>
        <v-card-title class="text-h5">
          {{ editingEmployment ? "Редактировать" : "Создать" }}
        </v-card-title>
        <v-card-text>
          <v-form ref="employmentForm" v-model="valid" @submit.prevent="saveEmployment">
            <v-text-field
              v-model="employmentForm.year"
              label="Год"
              type="number"
              clearable
              :rules="[rules.required]"
            ></v-text-field>
            <v-text-field
              v-model="employmentForm.number_of_employees"
              label="Численность сотрудников"
              type="number"
              clearable
              :rules="[rules.required]"
            ></v-text-field>
            <v-text-field
              v-model="employmentForm.salary"
              label="Средняя зарплата"
              type="number"
              clearable
              :rules="[rules.required]"
            ></v-text-field>
            <v-select v-model="employmentForm.okved_section_id"
                :items="okvedSections()"
                item-title="name"
                item-value="id"
                label="ОКВЭД"
                clearable
                :rules="[rules.required]"
                
                >
                
            </v-select>
          </v-form>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text @click="closeEditDialog">Отмена</v-btn>
          <v-btn color="primary" :disabled="!valid" @click="saveEmployment">Сохранить</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  
    <v-dialog v-model="confirmDeleteDialog" max-width="400px">
      <v-card>
        <v-card-title class="text-h5">Подтвердите удаление</v-card-title>
        <v-card-text>
          Вы уверены, что хотите удалить запись за {{ employmentToDelete?.year }} год?
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
        headers: [
          { title: "Год", key: "year" },
          { title: "Численность сотрудников", key: "number_of_employees" },
          { title: "Средняя зарплата", key: "salary" },
          { title: "", key: "edit", sortable: false },
          { title: "", key: "delete", sortable: false },
        ],
        confirmDeleteDialog: false,
        editDialog: false,
        employmentToDelete: null,
        editingEmployment: null,
        okveds_list: [],
        employmentForm: {
          year: "",
          number_of_employees: "",
          okved_section_id: "",
          salary: "",
        },
        valid: false,
        rules: {
          required: (value) => !!value || "Это поле обязательно",
        },
      };
    },
    computed: {
      groupBy() {
      return [
        { key: "okved_section.name", order: "asc" },
      ];
    },
    },
    methods: {
        okvedSections() {
      return this.$store.state.okved.data;
    },
    ...mapActions({
      getOkvedSections: "okved/getOkvedSections",
    }),
        employmentMinstat() {
        return this.$store.state.employment_minstat.data;
      },
      ...mapActions({
        getEmploymentMinstat: "employment_minstat/getEmploymentMinstat",
        createEmploymentMinstat: "employment_minstat/createEmploymentMinstat",
        updateEmploymentMinstat: "employment_minstat/updateEmploymentMinstat",
        deleteEmploymentMinstat: "employment_minstat/deleteEmploymentMinstat",
      }),
      openCreateDialog() {
        this.editingEmployment = null;
        this.employmentForm = { year: "", number_of_employees: "", okved_section_id: "", salary: "" };
        this.editDialog = true;
      },
      openEditDialog(employment) {
        this.editingEmployment = employment;
        this.employmentForm = { ...employment };
        this.editDialog = true;
      },
      closeEditDialog() {
        this.editDialog = false;
        this.employmentForm = { year: "", number_of_employees: "", okved_section_id: "", salary: "" };
      },
      async saveEmployment() {
        const formData = { ...this.employmentForm };
        if (this.editingEmployment) {
          formData.id = this.editingEmployment.id;
          await this.updateEmploymentMinstat(formData);
        } else {
          await this.createEmploymentMinstat(formData);
        }
        await this.getEmploymentMinstat();
        this.closeEditDialog();
      },
      confirmDelete(employment) {
        this.employmentToDelete = employment;
        this.confirmDeleteDialog = true;
      },
      closeConfirmDialog() {
        this.confirmDeleteDialog = false;
        this.employmentToDelete = null;
      },
      async deleteConfirmed() {
        if (this.employmentToDelete) {
          await this.deleteEmploymentMinstat(this.employmentToDelete.id);
          await this.getEmploymentMinstat();
          this.closeConfirmDialog();
        }
      },
    },
    async created() {
      await this.getEmploymentMinstat();
      await this.getOkvedSections();
      
    },
  };
  </script>
  