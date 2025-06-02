<template>
  <div class="upload-container">
    <h2>Upload New Track</h2>
    
    <form @submit.prevent="submitTrack">
      <div class="form-group">
        <label>Track Name*</label>
        <input v-model="trackData.name" type="text" required>
      </div>
      
      <!-- <div class="form-group">
        <label>Artist ID*</label>
        <input v-model.number="trackData.artist_id" type="number" required>
      </div> -->
      
      <div class="form-group">
        <label>Genre ID</label>
        <input v-model.number="trackData.genre_id" type="number">
      </div>
      
      <div class="form-group">
        <label>Release Date*</label>
        <input v-model="trackData.release_date" type="date" required>
      </div>

      <div class="form-group">
        <label>Cover (png, jpeg)</label>
        <input 
          type="file" 
          accept="image/png, image/gif, image/jpeg" 
          @change="handleFileChangeCover"
          required
        >
      </div>
      
      <div class="form-group">
        <label>Audio File* (MP3)</label>
        <input 
          type="file" 
          accept="audio/mpeg" 
          @change="handleFileChangeAudio"
          required
        >
      </div>
      
      <button type="submit" :disabled="isLoading">
        {{ isLoading ? 'Uploading...' : 'Upload Track' }}
      </button>
      
      <div v-if="error" class="error">{{ error }}</div>
      <div v-if="success" class="success">Track uploaded successfully!</div>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import apiClient from '@/api/axios';
import { getUserID } from '../router';

const trackData = ref({
  name: '',
  genre_id: null,
  release_date: new Date().toISOString().split('T')[0]
});

const audioFile = ref(null);
const coverFile = ref(null);
const isLoading = ref(false);
const error = ref(null);
const success = ref(false);

const handleFileChangeAudio = (e) => {
  audioFile.value = e.target.files[0];
};
const handleFileChangeCover = (e) => {
  coverFile.value = e.target.files[0];
};

const submitTrack = async () => {
  if (!audioFile.value) {
    error.value = 'Please select an audio file';
    return;
  }

  isLoading.value = true;
  error.value = null;
  success.value = false;

  try {
    const formData = new FormData();
    formData.append('track_file', audioFile.value);
    formData.append('cover_file', coverFile.value);
    var user_id = getUserID(localStorage.getItem("token")).id;
    const response = await apiClient.post('/track/single/', formData, {
      params: {
        name: trackData.value.name,
        artist_id: user_id,
        genre_id: trackData.value.genre_id || undefined,
        release_date: trackData.value.release_date
      },
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    });

    success.value = true;
    resetForm();
  } catch (err) {
    error.value = err.response?.data?.detail || 'Upload failed';
  } finally {
    isLoading.value = false;
  }
};

const resetForm = () => {
  trackData.value = {
    name: '',
    artist_id: null,
    genre_id: null,
    release_date: new Date().toISOString().split('T')[0]
  };
  audioFile.value = null;
};
</script>

<style scoped>
.upload-container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
}

.form-group {
  margin-bottom: 15px;
}

label {
  display: block;
  margin-bottom: 5px;
}

input[type="text"],
input[type="number"],
input[type="date"],
input[type="file"] {
  width: 100%;
  padding: 8px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

button {
  background-color: #42b983;
  color: white;
  padding: 10px 15px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.error {
  color: red;
  margin-top: 10px;
}

.success {
  color: green;
  margin-top: 10px;
}
</style>