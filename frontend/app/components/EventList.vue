<template>
    <UContainer>
        <UCard v-if="events.data" v-for="event in events.data" :key="event.id" class="mb-4 max-w-md mx-auto"
        :ui="{
        header: 'p-0 sm:px-0', // Remove padding from header slot
        }">
            <template #header>
                <NuxtImg src="/img/event.jpg" alt="Здесь должна быть картинка..." class=" object-cover" />
            </template>

            <p class="text-2xl">{{ event.title }}</p>
            <p >{{ formatDate.isoToRu(event.starts_at) }}</p>

            <template #footer>
                <UButton color="primary" block @click="() => console.log(`Registering for event ${event.id}`)">
                    Зарегистрироваться
                </UButton>
            </template>
        </UCard>
        <UProgress v-else animation="swing" />
    </UContainer>
</template>

<script setup>

const formatDate = useDateConverter()
const toast   = useToast()

const events = useEventsStore()



  try {
    await events.fetchEvents()
  } catch (err) {
    console.error(err)
    if (err instanceof Error) {
      toast.add({ title: 'Ошибка', description: err.message, color: 'error' })
      events.data = []
    } else {
      toast.add({ title: 'Ошибка', description: 'Произошла непредвиденная ошибка', color: 'error' })
        events.data = []
    }
  } finally {

  }
</script>
