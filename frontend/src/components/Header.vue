<template>
    <header>
        <div class="left-group">
            <router-link to="/" exact-active-class="active">
                <div class="logo">
                    <span class="icon icon-logo"></span>Slay
                </div>
            </router-link>
            <nav class="main-nav">
                <router-link to="/" exact-active-class="active">
                    <span class="icon icon-home"></span>
                    Home
                </router-link>
                <router-link to="/playlists" active-class="active">
                    <span class="icon icon-playlists"></span>
                    Playlists
                </router-link>
                <router-link to="/liked" active-class="active">
                    <span class="icon icon-liked"></span>
                    Liked
                </router-link>
                <router-link to="/profile" active-class="active">
                    <span class="icon icon-user"></span>
                    Profile
                </router-link>
            </nav>
        </div>
        <div class="right-group">
            <button @click="openSearchModal" class="search-btn">
                <span class="icon icon-search"></span>
            </button>
        </div>
        
        <SearchModal 
          :isOpen="isSearchModalOpen" 
          @close="closeSearchModal" 
        />
    </header>
</template>

<script setup>
import { ref } from 'vue';
import SearchModal from '@/components/SearchModal.vue';

const isSearchModalOpen = ref(false);

const openSearchModal = () => {
  isSearchModalOpen.value = true;
};

const closeSearchModal = () => {
  isSearchModalOpen.value = false;
};
</script>

<style>
@import '../assets/css/styles.css';
a {
  text-decoration: none;
}
.search-btn {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 5px;
}

.search-btn:hover {
  opacity: 0.8;
}
</style>