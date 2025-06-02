<template>
    <header>
        <div class="left-group">
            <router-link to="/" exact-active-class="active">
                <div class="logo">
                    <span class="logo-sl">SL</span><span class="logo-ay">AY</span>
                </div>
            </router-link>
            <nav class="main-nav">
                <router-link to="/" exact-active-class="active">
                    <span class="icon icon-home"></span>
                    Home
                </router-link>
                <!-- <router-link to="/playlists" active-class="active">
                    <span class="icon icon-playlists"></span>
                    Playlists
                </router-link> -->
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
            <button @click="openUploadModal" class="search-btn">
                <span class="icon icon-upload"></span>
            </button>
        </div>
        
        <SearchModal 
          :isOpen="isSearchModalOpen" 
          @close="closeSearchModal" 
        />

        <UploadModal 
          :isOpen="isUploadModalOpen" 
          @close="closeUploadModal" 
        />
        
    </header>
</template>

<script setup>
import { ref } from 'vue';
import SearchModal from '@/components/SearchModal.vue';
import UploadModal from '@/components/UploadModal.vue';

const isSearchModalOpen = ref(false);
const isUploadModalOpen = ref(false);

const openSearchModal = () => {
  isSearchModalOpen.value = true;
};

const closeSearchModal = () => {
  isSearchModalOpen.value = false;
};

const openUploadModal = () => {
  isUploadModalOpen.value = true;
};

const closeUploadModal = () => {
  isUploadModalOpen.value = false;
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

.icon-upload {
  display: inline-block;
  width: 20px;
  height: 20px;
  background-color: currentColor;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z'/%3E%3C/svg%3E") no-repeat center;
}

.logo {
    display: flex;
    align-items: center;
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -1px;
    color: white;
    transition: all 0.3s ease;
    position: relative;
}

.logo-sl {
    color: #E50914;
    display: inline-block;
    transition: all 0.4s cubic-bezier(0.68, -0.6, 0.32, 1.6);
    transform-origin: left center;
    z-index: 2;
    position: relative;
}

.logo-ay {
    transition: all 0.3s ease;
    position: relative;
    margin-left: -8px;
    z-index: 1;
}

.logo:hover .logo-sl {
    transform: scale(1.2) rotate(-10deg);
    color: #ff1a1a;
    text-shadow: 0 0 15px rgba(229, 9, 20, 0.4);
    z-index: 3;
}

.logo:hover .logo-ay {
    transform: translateX(8px);
    color: rgba(229, 9, 20, 0.7);
    z-index: 1;
}

.logo:hover .logo-sl::after {
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 100%;
    height: 2px;
    background: linear-gradient(90deg, #E50914, transparent);
    animation: wave 0.6s ease;
    z-index: -1;
}

@keyframes wave {
    0% { transform: scaleX(0); opacity: 0; }
    50% { transform: scaleX(1); opacity: 1; }
    100% { transform: scaleX(0); opacity: 0; }
}

</style>