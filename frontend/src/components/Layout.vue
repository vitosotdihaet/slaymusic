<script setup>
import { useRoute } from 'vue-router';
import { ref, watchEffect } from 'vue';
import Player from '@/components/Player.vue';
const route = useRoute();
const isPlayerExist = ref(false);
watchEffect(() => {
    isPlayerExist.value = route.meta.player || false;
    console.log("Current route meta:", route.meta);
});
</script>

<template>
    <div>
        <Player v-if="isPlayerExist" />
        <router-view />
    </div>
</template>
