<template>
    <div class="post-item">
        <div class="post-item-title">{{ title }}</div>
        <div class="post-item-body">{{ body }}</div>
    </div>
</template>
<script>
export default {
    name: "post-item",
    props: {
        title:{
            type: String,
            required: true,
        },
        body:{
            type: String,
            required: true,
        },
    }
}
</script>


<style>
    
</style>