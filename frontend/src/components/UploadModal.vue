<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="search-header">
        <h2>Upload Track</h2>
        <button class="close-btn" @click="closeModal">
          &times;
        </button>
      </div>
      
      <div class="upload-form">
        <div class="form-group">
          <label>Track Name*</label>
          <input 
            type="text" 
            v-model="trackData.name" 
            placeholder="Enter track name"
            required
          >
        </div>
        
        <div class="form-group">
          <label>Genre</label>
          <input 
            type="text" 
            v-model="trackData.genre" 
            placeholder="Enter genre"
          >
        </div>
        
        <div class="form-group">
          <label>Release Date*</label>
          <input 
            type="date" 
            v-model="trackData.release_date" 
            required
          >
        </div>

        <div class="form-group file-upload">
          <label>Cover Image</label>
          <div class="file-input-wrapper">
            <input 
              type="file" 
              accept="image/png, image/jpeg" 
              @change="handleFileChangeCover"
            >
            <span class="file-label">{{ coverFile ? coverFile.name : 'Select file' }}</span>
          </div>
        </div>
        
        <div class="form-group file-upload">
          <label>Audio File*</label>
          <div class="file-input-wrapper">
            <input 
              type="file" 
              accept="audio/mpeg" 
              @change="handleFileChangeAudio"
              required
            >
            <span class="file-label">{{ audioFile ? audioFile.name : 'Select file' }}</span>
          </div>
        </div>
        
        <button 
          type="submit" 
          class="upload-btn"
          @click="submitTrack"
          :disabled="isLoading"
        >
          <span v-if="isLoading" class="loading-spinner"></span>
          {{ isLoading ? 'Uploading...' : 'Upload Track' }}
        </button>
        
        <div v-if="error" class="error-message">{{ error }}</div>
        <div v-if="success" class="success-message">{{ success }}</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/api/axios';
import { getUserID } from '../router';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);

const trackData = ref({
  name: '',
  genre: '',
  release_date: new Date().toISOString().split('T')[0]
});

const audioFile = ref(null);
const coverFile = ref(null);
const isLoading = ref(false);
const error = ref(null);
const success = ref(null);

const handleFileChangeAudio = (e) => {
  audioFile.value = e.target.files[0];
};

const handleFileChangeCover = (e) => {
  coverFile.value = e.target.files[0];
};

const closeModal = () => {
  emit('close');
  resetForm();
};

const submitTrack = async () => {
  if (!audioFile.value) {
    error.value = 'Please select an audio file';
    return;
  }

  isLoading.value = true;
  error.value = null;
  success.value = null;

  try {
    const formData = new FormData();
    formData.append('track_file', audioFile.value);
    if (coverFile.value) formData.append('cover_file', coverFile.value);
    
    const user_id = getUserID(localStorage.getItem("token")).id;
    
    await apiClient.post('/track/single/', formData, {
      params: {
        name: trackData.value.name,
        artist_id: user_id,
        genre: trackData.value.genre || undefined,
        release_date: trackData.value.release_date
      },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    success.value = 'Track uploaded successfully!';
    setTimeout(() => {
      closeModal();
    }, 2000);
  } catch (err) {
    error.value = err.response?.data?.detail || 'Upload failed';
  } finally {
    isLoading.value = false;
  }
};

const resetForm = () => {
  trackData.value = {
    name: '',
    genre: '',
    release_date: new Date().toISOString().split('T')[0]
  };
  audioFile.value = null;
  coverFile.value = null;
  error.value = null;
  success.value = null;
};
</script>

<style scoped>
/* Основные стили модального окна (как у поиска) */
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
  max-width: 500px;
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

/* Стили формы */
.upload-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  color: rgba(255, 255, 255, 0.8);
  font-size: 0.9rem;
}

.form-group input[type="text"],
.form-group input[type="date"] {
  padding: 12px 15px;
  background: #282828;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: white;
  font-size: 0.95rem;
  outline: none;
}

.form-group input[type="text"]:focus,
.form-group input[type="date"]:focus {
  background: #383838;
}

/* Стили для загрузки файлов */
.file-upload {
  margin-top: 10px;
}

.file-input-wrapper {
  position: relative;
  overflow: hidden;
  display: flex;
  align-items: center;
}

.file-input-wrapper input[type="file"] {
  position: absolute;
  font-size: 100px;
  opacity: 0;
  right: 0;
  top: 0;
  cursor: pointer;
  width: 100%;
  height: 100%;
}

.file-label {
  flex: 1;
  padding: 12px 15px;
  background: #282828;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.file-input-wrapper:hover .file-label {
  background: #383838;
}

/* Кнопка загрузки */
.upload-btn {
  margin-top: 10px;
  background-color: #E50914;
  color: white;
  padding: 12px;
  border: none;
  border-radius: 6px;
  font-size: 1rem;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 8px;
}

.upload-btn:hover:not(:disabled) {
  background-color: #f40612;
}

.upload-btn:disabled {
  background-color: #666;
  cursor: not-allowed;
}

.loading-spinner {
  display: inline-block;
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  animation: spin 1s linear infinite;
}

/* Сообщения об ошибках/успехе */
.error-message {
  color: #ff4d4d;
  margin-top: 10px;
  font-size: 0.9rem;
}

.success-message {
  color: #4CAF50;
  margin-top: 10px;
  font-size: 0.9rem;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Адаптивность */
@media (max-width: 768px) {
  .modal-content {
    width: 90%;
    padding: 15px;
  }
  
  .search-header h2 {
    font-size: 1.5rem;
  }
}
</style>