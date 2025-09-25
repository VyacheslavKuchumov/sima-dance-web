
export const useEventsStore = defineStore('events', {
  state: () => ({
    data: [],
  }),
 
  actions: {
    async fetchEvents() {
        if (this.data.length > 0) return
        const config = useNuxtApp().$config
        const res = await $fetch(`${config.public.BACKEND_URL}/api/booking/events/`, {
            method: 'GET',
            credentials: 'include', // Include cookies for authentication
        })
        this.data = res.results
    },
  }
})
