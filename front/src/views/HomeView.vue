<template>
  <v-overlay
      :model-value="overlay"
      class="align-center justify-center"
    >
      <v-progress-circular
        color="primary"
        size="64"
        indeterminate
      ></v-progress-circular>
    </v-overlay>
  <v-card  v-if="user()" class="mx-auto" max-width="400" prepend-icon="mdi-account">
    <template v-slot:title>
      <span class="font-black">Пользователь {{ user().name }}</span>
    </template>
    <template v-if="user().role === 'admin'" v-slot:subtitle>
      {{ user().role }}
    </template>

    <v-card-text>
      Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed vel nisl sed massa venenatis consequat. Integer auctor mollis ex eu imperdiet. Praesent at vehicula sem. Nulla facilisi. Sed ultrices scelerisque ex eu maximus. Duis vulputate lobortis nisl a ullamcorper. Nullam ultrices ultrices lectus, quis varius ex porta nec.
    </v-card-text>
    
  </v-card>
</template>

<script>
import { mapActions, mapState } from "vuex";

export default {
  name: "HomeView",
  data() {
    return {
      overlay: false,
      hasUserInfo: false,

    };
  },
  computed: {},
  methods: {
    ...mapActions({
      getUser: "user/getUserByUid",
    }),

    user() {
      return this.$store.state.user.user;
    },

  },
  watch: {},
  async mounted() {
    this.overlay = true;
    this.uid = localStorage.getItem("uid");

    if (this.uid) {
      await this.getUser();

    }
    this.overlay = false;
  },
};
</script>
