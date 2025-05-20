import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const usePlayerStore = defineStore('player', () => {
  const audio = new Audio();
  console.log('Audio element created:', audio);
  audio.style.display = 'none';
  document.body.appendChild(audio);
  const isPlaying = ref(false);
  const isLiked = ref(false);
  const currentTime = ref(0);
  const duration = ref(1);
  const progress = ref(0);

  audio.src = '/bloodth.mp3';
  audio.preload = 'metadata';

  audio.addEventListener('timeupdate', () => {
    currentTime.value = audio.currentTime;
    duration.value = audio.duration || 1;
    progress.value = (currentTime.value / duration.value) * 100;
  });

  audio.addEventListener('error', () => {
    console.error('Audio error', audio.error);
  });

  function togglePlay() {
    if (audio.paused) {
      audio.play();
      isPlaying.value = true;
    } else {
      audio.pause();
      isPlaying.value = false;
    }
  }

  function seekTo(percent) {
    audio.currentTime = (percent / 100) * duration.value;
  }

  function formatTime(seconds) {
    const min = Math.floor(seconds / 60);
    const sec = Math.floor(seconds % 60);
    return `${min}:${sec < 10 ? '0' : ''}${sec}`;
  }

  const formattedTime = computed(() => formatTime(currentTime.value));

  return {
    isPlaying,
    isLiked,
    progress,
    currentTime,
    duration,
    formattedTime,
    togglePlay,
    seekTo,
    audio,
  };
});
