<template>
    <UCard class="h-full w-full" shadow="lg" rounded="md" >
        <template #header>
            <h2 class="text-lg font-medium">{{ label }}</h2>
        </template>
        <div ref="panzoomContainer" class="h-full w-full">
            <slot />
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

const panzoomContainer = ref(null)

onMounted(() => {
    if (panzoomContainer.value) {
        const elem = panzoomContainer.value
        const panzoom = Panzoom(elem, {
            maxZoom: 3,
            minZoom: 0.5,
            smoothScroll: true,
            bounds: true,
            boundsPadding: 0.5,
        })
        elem.parentElement.addEventListener('wheel', panzoom.zoomWithWheel)
    }
})


</script>