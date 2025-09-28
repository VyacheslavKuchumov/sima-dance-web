<template>
    <UContainer class="h-full w-full border">
        <div ref="panzoomContainer" class="h-full w-full">
            <slot />
        </div>
    </UContainer>
</template>

<script setup>
import Panzoom from '@panzoom/panzoom'

const panzoomContainer = ref(null)

onMounted(() => {
    if (panzoomContainer.value) {
        Panzoom(panzoomContainer.value, {
            maxZoom: 3,
            minZoom: 0.5,
            smoothScroll: true,
            bounds: true,
            boundsPadding: 0.5,
        })
    }
})

</script>