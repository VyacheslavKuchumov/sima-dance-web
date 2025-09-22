<template>
    <v-dialog>

            <v-card class="pa-4" max-width="400">
                <v-card-title class="text-h5">Ошибка</v-card-title>
                <v-card-text>{{ message }}</v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn color="primary" text @click="$emit('update:visible', false)">Закрыть</v-btn>
                </v-card-actions>
            </v-card>

        
    </v-dialog>
</template>
<script setup>
defineProps({

    message: {
        type: String,
        required: true
    }
})
</script>
