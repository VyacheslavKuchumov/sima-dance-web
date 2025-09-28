<template>
    <UContainer>
    <!-- show loader while fetching -->
    <UProgress v-if="pending" animation="swing" />
      <DraggableContainer v-else>
        {{ seats }}
      </DraggableContainer>
      {{ seats }}
</UContainer>
</template>

<script setup>

const props = defineProps({
  event_id: Number,
})

const config = useRuntimeConfig()

const toast = useToast()


const { data, pending, error } = useFetch(`${config.public.BACKEND_URL}/api/booking/events/${props.event_id}/seatmap/`, {
  // automatic fetch on setup; remove or change options if needed
  // e.g. headers, credentials, baseURL, etc.
})

const seats = computed(() => {
  return data.value ?? []
})

if (error.value){
  toast.add({ title: 'Ошибка', description: `Не удалось загрузить ${error.value}`, color: 'error' })
}
</script>