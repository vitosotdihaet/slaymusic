<script setup>
import { ref } from 'vue';
import { usePlayerStore } from '@/stores/player';
import { computed } from 'vue';
import { getUserID } from '../router';
import { likeTrack, unlikeTrack, isLiked } from '../router';

const player = usePlayerStore();
const imageError = ref(false);

const handleImageError = () => {
  player.coverUrl = '';
};
var userID = getUserID(localStorage.getItem("token"));
const toggleLike = async (track) => {  
  track.isLiked = await isLiked(track.id, userID);
  if(!track.isLiked) {
    likeTrack(track.id, userID);
    track.isLiked = true;
  } else {
    unlikeTrack(track.id, userID);
    track.isLiked = false;
  }
};

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
    <div class="floating-player">
        <div class="player-content">
            <div class="track-info">
                <img 
                    class="cover-mini" 
                    :src="player.coverUrl" 
                    alt="Cover"
                    @error="handleImageError"
                    v-show="player.coverUrl != ''"
                    />
                <div v-if="player.coverUrl == ''" class="cover-mini cover-fallback">#</div>
                <div class="text">
                    <strong>{{ player.title }}</strong>
                    <small> {{player.author }}</small>
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
                <input type="range" min="0" max="100" v-model="player.progress" 
                       @input="player.seekTo(player.progress)" :style="progressBarStyle" />
            </div>

            <div class="other-controls">
                <button class="btn" @click="toggleLike(player.playerTrack)">
                    <span :class="['icon', 'icon-like', { liked: player.playerTrack.isLiked }]"></span>
                </button>
                <!-- <button class="btn"><span class="icon icon-add"></span></button> -->
                <!-- <button class="btn"><span class="icon icon-menu"></span></button> -->
            </div>
        </div>
    </div>
</template>

<style scoped>

/* fallback */
.cover-fallback {
  width: 50px;
  height: 50px;
  border-radius: 8px;
  margin-right: 15px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #333;
  color: white;
  font-weight: bold;
}

@media (max-width: 768px) {
  .cover-fallback {
    width: 40px;
    height: 40px;
    margin-right: 10px;
  }
}

.floating-player {
    position: fixed;
    bottom: 20px;
    left: 50%;
    transform: translateX(-50%);
    width: 90%;
    max-width: 800px;
    background: rgba(24, 24, 24, 0.95);
    border-radius: 20px;
    padding: 10px 20px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    z-index: 1000;
    display: flex;
    align-items: center;
    transition: all 0.3s ease;
}

.floating-player:hover {
    box-shadow: 0 15px 40px rgba(0, 0, 0, 0.7);
    transform: translateX(-50%) scale(1.02);
}

.player-content {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.track-info {
    display: flex;
    align-items: center;
    width: 200px;
}

.cover-mini {
    width: 50px;
    height: 50px;
    border-radius: 8px;
    margin-right: 15px;
    object-fit: cover;
}

.text {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.text strong {
    font-size: 0.9rem;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.text small {
    font-size: 0.7rem;
    opacity: 0.7;
    margin-top: 2px;
}

.controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.controls .btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: background 0.2s ease;
}

.controls .btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.progress {
    flex-grow: 1;
    margin: 0 20px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.time {
    font-size: 0.7rem;
    opacity: 0.8;
    min-width: 40px;
}

input[type=range] {
    -webkit-appearance: none;
    width: 100%;
    height: 4px;
    border-radius: 2px;
    cursor: pointer;
    flex-grow: 1;
}

input[type=range]::-webkit-slider-thumb {
    -webkit-appearance: none;
    appearance: none;
    width: 12px;
    height: 12px;
    background: #E50914;
    border-radius: 50%;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.2s ease;
}

input[type=range]:hover::-webkit-slider-thumb {
    opacity: 1;
}

.other-controls {
    display: flex;
    align-items: center;
    gap: 10px;
}

.other-controls .btn {
    background: none;
    border: none;
    cursor: pointer;
    padding: 8px;
    border-radius: 50%;
    transition: background 0.2s ease;
}

.other-controls .btn:hover {
    background: rgba(255, 255, 255, 0.1);
}

.icon {
    display: inline-block;
    width: 20px;
    height: 20px;
    background-size: cover;
}

.icon-like.liked {
    filter: brightness(0) saturate(100%) invert(27%) sepia(89%) saturate(3733%) hue-rotate(347deg) brightness(90%) contrast(97%);
}

@media (max-width: 768px) {
    .floating-player {
        width: 95%;
        padding: 8px 15px;
    }
    
    .track-info {
        width: 150px;
    }
    
    .cover-mini {
        width: 40px;
        height: 40px;
        margin-right: 10px;
    }
    
    .progress {
        margin: 0 10px;
    }
    
    .time {
        display: none;
    }
}

@media (max-width: 576px) {
    .floating-player {
        bottom: 10px;
        border-radius: 15px;
    }
    
    .text strong {
        font-size: 0.8rem;
    }
    
    .controls {
        gap: 5px;
    }
    
    .other-controls {
        display: none;
    }
}
</style>