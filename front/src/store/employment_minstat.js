import instance from "@/middlewares";


export default {
  name: "employment_minstat",
  state: () => ({
    data: null,

  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },

  },
  actions: {
    // employment minsat crud
    // get employment minsat
    async getEmploymentMinstat({ commit }) {
        try {
            const response = await instance.get("/api/employment_minstat");
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },
    

    // create employment minsat
    // year: int
    // number_of_employees: float
    // okved_section_id: int
    // salary: float
    async createEmploymentMinstat({}, input) {
        try {
            const { year, number_of_employees, okved_section_id, salary } = input;
            console.log(input);
            const response = await instance.post("/api/employment_minstat", { year: parseInt(year), number_of_employees: parseFloat(number_of_employees), salary: parseFloat(salary), okved_section_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },
    

    // update employment minsat
    // year: int
    // number_of_employees: float
    // okved_section_id: int
    async updateEmploymentMinstat({}, input) {
        try {
            const { id, year, number_of_employees, salary, okved_section_id } = input;
            const response = await instance.put(`/api/employment_minstat/${id}`, { year, salary, number_of_employees, okved_section_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete employment minsat
    async deleteEmploymentMinstat({}, id) {
        try {
            const response = await instance.delete(`/api/employment_minstat/${id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },


},

namespaced: true,
};
