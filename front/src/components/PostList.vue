<template>
    <div class="post-list">
        <div v-for="(post, index) in posts" :key="index">
            <PostItem :body="post.body" :title="post.title" />
        </div>
    </div>
</template>
<script>
import PostItem from './PostItem.vue';
export default {
    name: 'post-list',
    props: {
        posts: {
            type: Array,
            required: true
        }
    },
    components: { PostItem }
}
</script>

<style>

</style>