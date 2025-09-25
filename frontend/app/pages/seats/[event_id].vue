<template>
    {{ seats.data }}
</template>

<script setup>


    const route = useRoute()
    const event_id = computed(() => route.params.event_id)

    const seats = useSeatsStore()
    seats.fetchSeats(event_id.value)
</script>
