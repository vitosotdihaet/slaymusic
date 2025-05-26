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
          @keyup.enter="performSearch"
        >
        <button class="search-btn" @click="performSearch">
          <span class="icon icon-search"></span>
        </button>
      </div>
      
      <div class="search-results" v-if="results.length">
        <div class="result-item" v-for="item in results" :key="item.id">
          {{ item.name }} - {{ item.artist }}
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const searchQuery = ref('');
const results = ref([]);
const searchInput = ref(null);

const closeModal = () => {
  emit('close');
};

const performSearch = async () => {
  if (!searchQuery.value.trim()) return;
  
  try {
    // Здесь будет запрос к API
    console.log('Searching for:', searchQuery.value);
    // Временные моковые данные
    results.value = [
      { id: 1, name: 'Song 1', artist: 'Artist 1' },
      { id: 2, name: 'Song 2', artist: 'Artist 2' }
    ];
  } catch (error) {
    console.error('Search error:', error);
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
@import '../assets/css/styles.css';
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: flex-start;
  padding-top: 100px;
  z-index: 1000;
}

.modal-content {
  background-color: #1e1e1e;
  padding: 20px;
  border-radius: 8px;
  width: 500px;
  max-width: 90%;
  max-height: 80vh;
  overflow-y: auto;
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 24px;
  cursor: pointer;
}

.search-input {
  display: flex;
  margin-bottom: 20px;
}

.search-input input {
  flex: 1;
  padding: 10px 15px;
  border-radius: 20px 0 0 20px;
  border: none;
  background: #333;
  color: white;
}

.search-btn {
  background: #E50914;
  border: none;
  border-radius: 0 20px 20px 0;
  padding: 0 15px;
  cursor: pointer;
}

.search-results {
  margin-top: 20px;
}

.result-item {
  padding: 10px;
  border-bottom: 1px solid #333;
  cursor: pointer;
}

.result-item:hover {
  background: #333;
}
</style>