import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { BackendURL } from '../api/axios';

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
  const title = ref("SLAY ROCK");
  const author = ref("Eternxlkz");
  const coverUrl = ref("slayrock.png");
  const playerTrack = ref({
    isLiked: false,
  });

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

  function setTrack(track) {
    playerTrack.value = track;
    title.value = track.name;
    author.value = track.artist.name;
    audio.src = BackendURL(track.audioUrl);
    coverUrl.value = track.coverUrl;
    audio.play();
    isPlaying.value = true;
    console.log("set track", track);
    console.log("audio", audio);
  }

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
    title,
    author,
    isPlaying,
    isLiked,
    progress,
    currentTime,
    duration,
    formattedTime,
    togglePlay,
    seekTo,
    audio,
    setTrack,
    coverUrl,
    playerTrack,
  };
});
