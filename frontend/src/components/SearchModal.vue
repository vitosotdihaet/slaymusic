<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="search-header">
        <h2>Search</h2>
        <button class="close-btn" @click="closeModal">
          &times;
        </button>
      </div>
      
      <div class="search-input">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search for songs, artists..." 
          ref="searchInput"
          @input="handleInput"
        >
        <button class="search-btn" @click="performSearch">
          <span class="icon icon-search"></span>
        </button>
      </div>
      
      <div class="search-status">
        <div v-if="isLoading" class="loading">Searching...</div>
        <div v-else-if="error" class="error">{{ error }}</div>
        <div v-else-if="!results.length && searchQuery" class="empty">No results found</div>
      </div>
      
      <div class="search-results" v-if="results.length">
        <div class="result-list">
          <div 
            class="result-item"
            v-for="track in results" 
            :key="track.id"
            @click="playTrack(track)"
          >
            <div class="item-cover">
              <img :src="track.coverUrl" @error="hideErrorImage" />
              <button class="btn-play">
                <span class="icon icon-play-white"></span>
              </button>
            </div>

            <div class="item-info">
              <div class="info-main">
                <h3>{{ track.name }}</h3>
                <p>{{ track.artist.name }}</p>
              </div>

              <div class="item-actions">
                <button class="btn-like" @click.stop="toggleLike(track)">
                  <span :class="['icon', 'icon-like', { liked: track.isLiked }]"></span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import { usePlayerStore } from '@/stores/player';
import { debounce } from 'lodash-es';
import { BackendURL } from '@/api/axios';
import apiClient from '@/api/axios';
import { getTracksByQuery, getUserID, likeTrack, unlikeTrack, isLiked } from '../router';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const player = usePlayerStore();
const searchQuery = ref('');
const results = ref([]);
const searchInput = ref(null);
const isLoading = ref(false);
const error = ref(null);
const debounceTimeout = ref(null);
const userID = ref(null);

const closeModal = () => {
  emit('close');
};
userID.value = getUserID(localStorage.getItem("token"));

const debounceSearch = debounce(() => {
  performSearch();
}, 300);

const handleInput = () => {
  clearTimeout(debounceTimeout.value);

  if (!searchQuery.value.trim()) {
    results.value = [];
    return;
  }
  
  debounceTimeout.value = setTimeout(() => {
    performSearch();
  }, 300);
};

const performSearch = async () => {
  if (!searchQuery.value.trim()) {
    results.value = [];
    return;
  }
  
  isLoading.value = true;
  error.value = null;
  
  try {
    results.value = await getTracksByQuery({
      name: searchQuery.value
    }, false);
    for(var i=0; i < results.value.length; i++) {
      results.value[i].isLiked = await isLiked(results.value[i].id, userID.value);
    }
  } catch (err) {
    console.error('Search error:', err);
    error.value = 'Failed to load search results';
    results.value = [];
  } finally {
    isLoading.value = false;
  }
};

const playTrack = (track) => {
  player.setTrack(track);
};

const toggleLike = async (track) => {
  track.isLiked = await isLiked(track.id, userID.value);
  if(!track.isLiked) {
    likeTrack(track.id, getUserID(localStorage.getItem("token")));
    track.isLiked = true;
  } else {
    unlikeTrack(track.id, getUserID(localStorage.getItem("token")));
    track.isLiked = false;
  }
};

const hideErrorImage = (e) => {
  try {
    e.target.style.display = "none";
  } catch (error) {
    console.log("Error hiding image:", error);
  }
};

watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    setTimeout(() => {
      searchInput.value?.focus();
    }, 100);
  } else {
    searchQuery.value = '';
    results.value = [];
  }
});
</script>

<style scoped>
.search-status {
  min-height: 20px;
  margin: 10px 0;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.loading {
  display: flex;
  align-items: center;
  gap: 8px;
}

.loading:before {
  content: "";
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #E50914;
  animation: spin 1s linear infinite;
}

.error {
  color: #E50914;
}

.empty {
  font-style: italic;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}



.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.9);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 50px;
  z-index: 1000;
  backdrop-filter: blur(5px);
}

.modal-content {
  background-color: #121212;
  padding: 25px;
  border-radius: 12px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.search-header h2 {
  color: white;
  font-size: 1.8rem;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 28px;
  cursor: pointer;
  opacity: 0.7;
  transition: opacity 0.2s;
}

.close-btn:hover {
  opacity: 1;
}

.search-input {
  display: flex;
  margin-bottom: 25px;
  position: relative;
}

.search-input input {
  flex: 1;
  padding: 12px 20px;
  border-radius: 25px;
  border: none;
  background: #282828;
  color: white;
  font-size: 1rem;
  outline: none;
}

.search-input input:focus {
  background: #383838;
}

.search-btn {
  position: absolute;
  right: 5px;
  top: 5px;
  background: #E50914;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: background 0.2s;
}

.search-btn:hover {
  background: #ff1a1a;
}

.icon-search {
  display: inline-block;
  width: 18px;
  height: 18px;
  background-color: white;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M15.5 14h-.79l-.28-.27a6.5 6.5 0 0 0 1.48-5.34c-.47-2.78-2.79-5-5.59-5.34a6.505 6.505 0 0 0-7.27 7.27c.34 2.8 2.56 5.12 5.34 5.59a6.5 6.5 0 0 0 5.34-1.48l.27.28v.79l4.25 4.25c.41.41 1.08.41 1.49 0 .41-.41.41-1.08 0-1.49L15.5 14zm-6 0C7.01 14 5 11.99 5 9.5S7.01 5 9.5 5 14 7.01 14 9.5 11.99 14 9.5 14z'/%3E%3C/svg%3E") no-repeat center;
}

.search-results {
  margin-top: 20px;
}

.result-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.result-item {
  display: flex;
  align-items: center;
  background: rgba(30, 30, 30, 0.7);
  border-radius: 8px;
  padding: 8px;
  transition: all 0.3s ease;
  cursor: pointer;
  position: relative;
  overflow: hidden;
  border: 1px solid transparent;
}

.result-item:hover {
  background: rgba(40, 40, 40, 0.9);
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
  border-color: rgba(255, 255, 255, 0.1);
}

.item-cover {
  position: relative;
  width: 50px;
  height: 50px;
  min-width: 50px;
  border-radius: 4px;
  overflow: hidden;
  background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
}

.item-cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.btn-play {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(229, 9, 20, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
  border: none;
}

.result-item:hover .btn-play {
  opacity: 1;
}

.icon-play-white {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: white;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M8 5v14l11-7z'/%3E%3C/svg%3E") no-repeat center;
}

.item-info {
  flex: 1;
  display: flex;
  align-items: center;
  padding: 0 12px;
  overflow: hidden;
}

.info-main {
  flex: 1;
  min-width: 0;
}

.info-main h3 {
  color: white;
  font-size: 0.95rem;
  margin: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info-main p {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.8rem;
  margin: 2px 0 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-actions {
  padding-right: 8px;
}

.btn-like {
  background: none;
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-like:hover {
  background: rgba(255, 255, 255, 0.1);
}

.icon-like {
  display: inline-block;
  width: 18px;
  height: 18px;
  background-color: white;
  opacity: 0.7;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E") no-repeat center;
  transition: all 0.2s ease;
}

.icon-like:hover {
  opacity: 1;
  transform: scale(1.1);
}

.icon-like.liked {
  filter: brightness(0) saturate(100%) invert(27%) sepia(89%) saturate(3733%) hue-rotate(347deg) brightness(90%) contrast(97%);
}

@media (max-width: 768px) {
  .modal-content {
    width: 90%;
    padding: 15px;
  }

  .result-item {
    padding: 6px;
  }

  .item-cover {
    width: 40px;
    height: 40px;
    min-width: 40px;
  }

  .info-main h3 {
    font-size: 0.85rem;
  }

  .info-main p {
    font-size: 0.75rem;
  }
}
</style>