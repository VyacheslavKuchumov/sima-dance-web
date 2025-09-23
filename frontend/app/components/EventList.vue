<template>
    <UContainer>
        <UCard v-for="event in events" :key="event.id" class="mb-4">
            <template #header>
                <p class="h-8">{{ event.name }} {{ formatDate.isoToRu(event.date) }}</p>
            </template>
            <img :src="event.image" alt="Event Image" class="w-full h-48 object-cover" />
            <template #footer>
                <UButton color="primary" block @click="() => console.log(`Registering for event ${event.id}`)">
                    Зарегистрироваться
                </UButton>
            </template>
        </UCard>
    </UContainer>
</template>

<script setup lang="ts">

const formatDate = useDateConverter()

const events = ref([
    { id: 1, name: 'Отчетный концерт', date: '2023-12-01', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGHaBRvhk8oP8nlTzKWHLl9nxxUxZ3UF43KA&s' },
    { id: 2, name: 'Новогодний бал', date: '2023-12-25', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGHaBRvhk8oP8nlTzKWHLl9nxxUxZ3UF43KA&s' },
    { id: 3, name: 'Весенний фестиваль', date: '2024-03-15', image: 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRGHaBRvhk8oP8nlTzKWHLl9nxxUxZ3UF43KA&s' },
]);
</script>
