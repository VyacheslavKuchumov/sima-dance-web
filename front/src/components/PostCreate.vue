<template>
    <div>
        <form @submit.prevent="createPost" class="post-create-form">

            <textarea type="text" class="post-create-input" rows="1" placeholder="Введите содержимое" required v-model="title"></textarea>
            <textarea type="text" class="post-create-input" rows="5" placeholder="Введите содержимое" required v-model="body"></textarea>
            <button class="post-create-button" type="submit">Создать пост</button>

        </form>
    </div>
</template>
<script>
export default {
    name: 'post-create',
    data() {
        return {
            title: '',
            body: ''
        }
    },
    methods: {
        createPost() {
            const post = {
                title: this.title,
                body: this.body
            }
            this.$emit('create', post)
        }
    },
}
</script>

<style>

</style>