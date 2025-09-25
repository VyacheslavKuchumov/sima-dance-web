
export const useSeatsStore = defineStore('seats', {
  state: () => ({
    data: [],
  }),
 
  actions: {
    async fetchSeats(event_id) {
        if (this.data.length > 0) return
        const config = useNuxtApp().$config
        const res = await $fetch(`${config.public.BACKEND_URL}/api/booking/events/${event_id}/seatmap/`, {
            method: 'GET',
            credentials: 'include', // Include cookies for authentication
        })
        this.data = res.results
    },
  }
})
