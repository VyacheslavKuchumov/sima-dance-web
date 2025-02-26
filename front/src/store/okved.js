import instance from "@/middlewares";


export default {
  name: "okved",
  state: () => ({
    data: null,

  }),
  mutations: {
    setData(state, data) {
      state.data = data;
    },

  },
  actions: {
    // okved sections crud
    // get okved sections
    async getOkvedSections({ commit }) {
        try {
            const response = await instance.get("/api/okved_sections");
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved section
    async createOkvedSection({}, input) {
        try {
            const { name, code } = input;
            const response = await instance.post("/api/okved_sections", { name, code });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved section
    async updateOkvedSection({}, input) {
        try {
            const { id, name, code } = input;
            const response = await instance.put(`/api/okved_sections/${id}`, { name, code });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved section
    async deleteOkvedSection({}, id) {
        try {
            const response = await instance.delete(`/api/okved_sections/${id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },



    // okved classes crud
    // get okved classes
    async getOkvedClasses({ commit }, id) {
        try {
            const response = await instance.get(`/api/okved/classes/${id}`);
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved class
    async createOkvedClass({}, input) {
        try {
            const { name, code, section_id } = input;
            console.log(input);
            const response = await instance.post("/api/okved/classes", { name, code, section_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved class
    async updateOkvedClass({}, input) {
        try {
            const { id, name, code, section_id } = input;
            const response = await instance.put("/api/okved/classes", { id, name, code, section_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved class
    async deleteOkvedClass({}, class_id) {
        try {
            const response = await instance.delete(`/api/okved/classes/${class_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },



    // okved subclasses crud
    // get okved subclasses
    async getOkvedSubclasses({ commit }, id) {
        try {
            const response = await instance.get(`/api/okved/subclasses/${id}`);
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved subclass
    async createOkvedSubclass({}, input) {
        try {
            const { name, code, class_id } = input;
            const response = await instance.post("/api/okved/subclasses", { name, code, class_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved subclass
    async updateOkvedSubclass({}, input) {
        try {
            const { id, name, code, class_id } = input;
            const response = await instance.put("/api/okved/subclasses", { id, name, code, class_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved subclass
    async deleteOkvedSubclass({}, subclass_id) {
        try {
            const response = await instance.delete(`/api/okved/subclasses/${subclass_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },


    // okved groups crud
    // get okved groups
    async getOkvedGroups({ commit }, id) {
        try {
            const response = await instance.get(`/api/okved/groups/${id}`);
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved group
    async createOkvedGroup({}, input) {
        try {
            const { name, code, subclass_id } = input;
            const response = await instance.post("/api/okved/groups", { name, code, subclass_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved group
    async updateOkvedGroup({}, input) {
        try {
            const { id, name, code, subclass_id } = input;
            const response = await instance.put("/api/okved/groups", { id, name, code, subclass_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved group
    async deleteOkvedGroup({}, group_id) {
        try {
            const response = await instance.delete(`/api/okved/groups/${group_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },


    // okved subgroups crud
    // get okved subgroups
    async getOkvedSubgroups({ commit }, id) {
        try {
            const response = await instance.get(`/api/okved/subgroups/${id}`);
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved subgroup
    async createOkvedSubgroup({}, input) {
        try {
            const { name, code, group_id } = input;
            const response = await instance.post("/api/okved/subgroups", { name, code, group_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved subgroup
    async updateOkvedSubgroup({}, input) {
        try {
            const { id, name, code, group_id } = input;
            const response = await instance.put("/api/okved/subgroups", { id, name, code, group_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved subgroup
    async deleteOkvedSubgroup({}, subgroup_id) {
        try {
            const response = await instance.delete(`/api/okved/subgroups/${subgroup_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },


    // okved activities crud
    // get okved activities
    async getOkvedActivities({ commit }, id) {
        try {
            const response = await instance.get(`/api/okved/activities/${id}`);
            if (response) return commit("setData", response.data);
        }
        catch (error) {
            console.log(error);
        }
    },

    // create okved activity
    async createOkvedActivity({}, input) {
        try {
            const { name, code, subgroup_id } = input;
            const response = await instance.post("/api/okved/activities", { name, code, subgroup_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // update okved activity
    async updateOkvedActivity({}, input) {
        try {
            const { id, name, code, subgroup_id } = input;
            const response = await instance.put("/api/okved/activities", { id, name, code, subgroup_id });
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

    // delete okved activity
    async deleteOkvedActivity({}, activity_id) {
        try {
            const response = await instance.delete(`/api/okved/activities/${activity_id}`);
            if (response.ok) return console.log("ok");
        }
        catch (error) {
            console.log(error);
        }
    },

  },

  namespaced: true,
};
