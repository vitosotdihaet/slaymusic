<script setup>
import { usePlayerStore } from '@/stores/player';
import { computed } from 'vue';

const player = usePlayerStore();

const progressBarStyle = computed(() => {
    let val = player.progress;
    let add = 0;
    if (val < 20) add = 0.5;
    else if (val > 90) add = -0.2;

    return {
        background: `linear-gradient(to right, #E50914 0%, #E50914 ${val + add}%, white ${val}%, white 100%)`
    };
});

</script>

<template>
    <footer class="player">
        <div class="track-info">
            <img class="cover-mini" src="slayrock.png" alt="Cover" />
            <div class="text">
                <strong>SLAY ROCK</strong>
                <small>Eternxlkz</small>
            </div>
        </div>

        <div class="controls">
            <button class="btn" @click="player.prevTrack"><span class="icon icon-prev"></span></button>
            <button class="btn" @click="player.togglePlay">
                <span :class="player.isPlaying ? 'icon icon-pause' : 'icon icon-play'"></span>
            </button>
            <button class="btn" @click="player.nextTrack"><span class="icon icon-next"></span></button>
        </div>

        <div class="progress">
            <span class="time">{{ player.formattedTime }}</span>
            <input type="range" min="0" max="100" v-model="player.progress" @input="player.seekTo(player.progress)"
                :style="progressBarStyle" />
        </div>

        <div class="other-controls">
            <button class="btn" @click="player.isLiked = !player.isLiked">
                <span :class="['icon', 'icon-like', { liked: player.isLiked }]"></span>
            </button>
            <button class="btn"><span class="icon icon-add"></span></button>
            <button class="btn"><span class="icon icon-menu"></span></button>
        </div>
    </footer>
</template>
