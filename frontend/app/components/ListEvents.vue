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

  
    <!-- Main Card with Toolbar and Cards for each Event -->
    <v-container class="elevation-0 mt-5 ml-auto mr-auto">
        <v-card max-width="800" class="elevation-0 mt-5 ml-auto mr-auto">
        <v-card-title class="text-wrap" align="center">
            Концерты
        </v-card-title>
    </v-card>

        <v-container v-if="events && events.length">
            <v-row
            v-for="item in events"
            :key="item.event_id"
            >
                <v-col>
                    <v-card class="ma-2 elevation-5 rounded-lg ml-auto mr-auto" max-width="500" min-height="300">
                        <!-- Event Image with Title Overlay gradient="to bottom, rgba(0,0,0,0.1), rgba(0,0,0,0.5)"--> 
                        <v-img :src="item.img_url" min-height="150px"  class="white--text align-end"/>
                        <v-card-title class="text-wrap">{{ item.event_name }}</v-card-title>
                        <!-- Event Details -->
                        <v-card-text>
                            <div>
                                <strong>Дата:</strong>
                                {{ isoToRu(item.event_date) }}
                            </div>
                        </v-card-text>
        
                        <!-- Action Buttons -->
                        <v-card-actions class="justify-center">
                            <v-btn color="primary" @click="goToEventBooking(item)">Купить билеты</v-btn>
                        </v-card-actions>
                    </v-card>
                </v-col>
            </v-row>
        </v-container>
  
        <!-- No Data Alert -->
        <v-alert v-else type="info" class="ma-4">
            Нет данных
        </v-alert>
    </v-container>

</template>

<script setup>

const { isoToRu } = useDateConverter()

const overlay = ref(false)

const events = ref([{
  event_id: 1,
  event_name: "Концерт группы А",
  event_date: "2023-10-15",
  img_url: "https://www.danceflavors.com/wp-content/uploads/2022/09/woman-and-little-girl-dancing-ballet-2022-02-01-22-39-15-utc.jpg"
}, {
  event_id: 2,
  event_name: "Концерт группы Б",
  event_date: "2023-11-20",
  img_url: "https://www.danceflavors.com/wp-content/uploads/2022/09/woman-and-little-girl-dancing-ballet-2022-02-01-22-39-15-utc.jpg"
}])

</script>