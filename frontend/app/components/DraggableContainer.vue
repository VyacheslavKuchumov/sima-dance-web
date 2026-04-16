<template>
    <UCard class="draggable-card h-full w-full min-w-0 overflow-hidden" shadow="lg" rounded="md">
        <template #header>
            <h2 class="text-lg font-medium">{{ label }}</h2>
        </template>
        <div ref="viewport" class="draggable-viewport">
            <div ref="panzoomContainer" class="draggable-content">
                <slot />
            </div>
        </div>
    </UCard>
</template>

<script setup>
import Panzoom from '@panzoom/panzoom'

const props = defineProps({
  label: {
    type: String,
    default: 'Draggable Container'
  }
})

const viewport = ref(null)
const panzoomContainer = ref(null)
let cleanupWheelListener = null

onMounted(() => {
    if (panzoomContainer.value && viewport.value) {
        const elem = panzoomContainer.value
        const panzoom = Panzoom(elem, {
            maxZoom: 3,
            minZoom: 0.5,
            smoothScroll: true,
            bounds: true,
            boundsPadding: 0.5,
        })
        const currentViewport = viewport.value
        currentViewport.addEventListener('wheel', panzoom.zoomWithWheel, { passive: false })
        cleanupWheelListener = () => currentViewport.removeEventListener('wheel', panzoom.zoomWithWheel)
    }
})

onBeforeUnmount(() => {
    cleanupWheelListener?.()
})

</script>

<style scoped>
.draggable-viewport {
    width: 100%;
    max-width: 100%;
    overflow: hidden;
    overscroll-behavior: contain;
    touch-action: none;
}

.draggable-content {
    display: inline-block;
    min-width: max-content;
    transform-origin: top left;
    will-change: transform;
}
</style>
