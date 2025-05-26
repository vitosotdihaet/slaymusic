<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router'
import apiClient from '@/api/axios';
import { getUserID } from '@/router/index';
import MainHeader from '@/components/Header.vue';
import { getArtistByID } from '../router';
import { usePlayerStore } from '@/stores/player';
const user_id = getUserID(localStorage.getItem("token"));
const playlists = ref([]);
const tracks = ref([]);
const router = useRouter();
const goToLikedPage = () => {
  router.push('/liked')
}

const player = usePlayerStore();
onMounted(async () => {
  try {
    const playlistsResponse = await apiClient.get("/playlists/", {}, {
      params: { author_id: user_id }
    });
    playlists.value = playlistsResponse.data;
    var playlist_fav_id = -1;
    playlists.value.forEach(element => {
      if(element.name == "fav"){
        playlist_fav_id = element.id;
        return;
      }
    });
    console.log(playlists.value, playlist_fav_id);

    if (playlist_fav_id != -1) {
      const tracksResponse = await apiClient.get(`/tracks/`, {
        params: { id: playlist_fav_id }
      });

      tracks.value = tracksResponse.data.map(track => ({
        ...track,
        artist: null,
        audioUrl: null,
      }));

      for (let i = 0; i < tracks.value.length; i++) {
        try {
          tracks.value[i].artist = await getArtistByID(tracks.value[i].artist_id);
        } catch (error) {
          tracks.value[i].artist = { name: 'Unknown Artist' };
        }
        try {
          tracks.value[i].audioUrl = `track/stream/?id=${tracks.value[i].id}`;
        } catch(error) {
          tracks.value[i].audioUrl = '';
        }
      }
      console.log(tracks);
    }
  } catch (error) {
    console.error("Ошибка при загрузке данных:", error);
  }
});
</script>

<template>
  <body>
    <MainHeader />

    <main>
      <section class="section">
        <h2>Liked Songs</h2>
        <div class="card-row">
          <div 
            class="track-card" 
            v-for="track in tracks" 
            :key="track.id"
            :style="{ '--rotation': Math.random() * 4 - 2 + 'deg' }"
          >
            <div class="card-content">
              <div class="cover">
                #
                <button class="btn-play">
                  <span class="icon icon-play-white" @click="player.setTrack(track);"></span>
                </button>
              </div>
              <div class="info">
                <div class="info-row">
                  <h3>{{ track.name }}</h3>
                  <div class="card-actions">
                    <span class="icon icon-like "></span>
                  </div>
                </div>              
                <p v-if="track.artist">{{ track.artist.name }}</p>
                <p v-else>Loading artist...</p>
              </div>
            </div>
          </div>
          <div 
            class="track-card more-card"
            :style="{ '--rotation': Math.random() * 4 - 2 + 'deg' }"
            @click="goToLikedPage"
          >
            <div class="card-content">
              <div class="more-icon">></div>
              <div class="info">
                <div class="info-row">
                  <h3>Go to liked</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

       <section class="section">
        <h2>Your Top Mixes</h2>
        <div class="card-row">
          <div class="card">
            <div class="cover">#
              <button class="btn-play">
                <span class="icon icon-play-white"></span>
              </button>
            </div>
            <div class="info">
              <div class="info-row">
                <h3>Rock Mix</h3>
                <div class="card-actions">
                  <span class="icon icon-like"></span>
                  <!-- <span class="icon icon-add"></span> -->
                </div>
              </div>
              <p>RHCP…</p>
            </div>
          </div>

        </div>
      </section>
    </main>
  </body>
</template>

<style scoped>

.more-card .card-content {
  background: linear-gradient(135deg, rgba(40,40,40,0.8) 0%, rgba(30,30,30,0.9) 100%);
}

.more-cover {
  background: linear-gradient(135deg, #3a3a3a 0%, #2a2a2a 100%) !important;
  position: relative;
}

.more-icon {
  font-size: 3rem;
  font-weight: 200;
  color: rgba(255,255,255,0.3);
  transition: all 0.3s ease;
}

.more-text {
  position: absolute;
  bottom: 15px;
  left: 0;
  right: 0;
  text-align: center;
  font-size: 1.2rem;
  font-weight: 600;
  color: rgba(255,255,255,0.7);
  opacity: 0;
  transform: translateY(10px);
  transition: all 0.3s ease;
}

.more-card:hover .more-icon {
  transform: scale(1.2);
  color: rgba(255,255,255,0.5);
}

.more-card:hover .more-text {
  opacity: 1;
  transform: translateY(0);
}

.more-card:hover .card-content {
  transform: translateZ(10px);
  box-shadow: 0 20px 40px rgba(0,0,0,0.4);
}

.more-card .btn-play {
  opacity: 1;
  bottom: 10px;
  transform: translateY(0);
  background: rgba(229, 9, 20, 0.7);
}

.more-card:hover .btn-play {
  background: #E50914;
}





.card-row {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
  padding: 20px 0;
}

.track-card {
  perspective: 1000px;
  transform: rotate(var(--rotation));
  transition: all 0.4s cubic-bezier(0.18, 0.89, 0.32, 1.28);
}

.card-content {
  position: relative;
  background: rgba(24, 24, 24, 0.7);
  border-radius: 12px;
  padding: 16px;
  transition: all 0.3s ease;
  transform-style: preserve-3d;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  border: 1px solid rgba(255, 255, 255, 0.1);
  overflow: hidden;
}

.track-card:hover {
  transform: rotate(0deg) translateY(-10px) scale(1.03);
  z-index: 10;
}

.track-card:hover .card-content {
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.4);
  background: rgba(24, 24, 24, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.cover {
  position: relative;
  width: 100%;
  aspect-ratio: 1;
  background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: rgba(255, 255, 255, 0.2);
  margin-bottom: 12px;
  overflow: hidden;
}

.btn-play {
  position: absolute;
  bottom: -40px;
  right: 10px;
  width: 40px;
  height: 40px;
  background: #E50914;
  border: none;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.3s ease;
  transform: translateY(10px);
  box-shadow: 0 4px 10px rgba(229, 9, 20, 0.3);
}

.track-card:hover .btn-play {
  opacity: 1;
  bottom: 10px;
  transform: translateY(0);
}

.btn-play:hover {
  transform: scale(1.1) translateY(0);
  background: #ff1a1a;
}

.icon-play-white {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: white;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M8 5v14l11-7z'/%3E%3C/svg%3E") no-repeat center;
}

.card-content::before,
.card-content::after {
  content: '';
  position: absolute;
  width: 30px;
  height: 30px;
  background: rgba(24, 24, 24, 0.9);
  z-index: -1;
  transition: all 0.3s ease;
}

.card-content::before {
  top: -15px;
  left: -15px;
  transform: rotate(45deg);
  box-shadow: -5px -5px 10px rgba(0, 0, 0, 0.1);
}

.card-content::after {
  bottom: -15px;
  right: -15px;
  transform: rotate(45deg);
  box-shadow: 5px 5px 10px rgba(0, 0, 0, 0.1);
}

.track-card:hover .card-content::before,
.track-card:hover .card-content::after {
  opacity: 0;
}

.info {
  color: white;
}

.info h3 {
  font-size: 1rem;
  margin: 0 0 4px 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.info p {
  font-size: 0.8rem;
  margin: 0;
  opacity: 0.7;
}

.icon-like {
  display: inline-block;
  width: 16px;
  height: 16px;
  background-color: white;
  opacity: 0.7;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z'/%3E%3C/svg%3E") no-repeat center;
  transition: all 0.2s ease;
}

.icon-like:hover {
  opacity: 1;
  transform: scale(1.1);
}
</style>