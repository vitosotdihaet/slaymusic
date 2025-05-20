<template>
    <div>
        <Player />
        <router-view />
    </div>
</template>

<script>
import Player from '@/components/Player.vue';
export default {
    components: { Player }
};
</script>
