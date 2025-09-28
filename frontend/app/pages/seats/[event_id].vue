<template>
    <SeatsList :event_id="event_id"/>
</template>

<script setup>
const route = useRoute()
const event_id = computed(() => route.params.event_id)
    
</script>
