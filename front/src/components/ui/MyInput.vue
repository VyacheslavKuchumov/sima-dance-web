<template>
    <input class="input" type="text" :values="value" @input="updateInput">
</template>
<script>
export default {
    name: 'my-input',
    props:{
        value:[String, Number]
    },
    methods: {
        updateInput(event){
            this.$emit('update:value', event.target.value)
        }
    },    
}
</script>
<style>
    .input{
        padding: 10px 15px;
        border: 1px solid black;
        
    }
    
</style>