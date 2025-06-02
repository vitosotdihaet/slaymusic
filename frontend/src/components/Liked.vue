<script setup>
import MainHeader from '@/components/Header.vue'
import { ref, onMounted } from 'vue'
import { usePlayerStore } from '@/stores/player'
import { getFavPlaylistID, getTracksByQuery, getUserID } from '../router'
const tracks = ref([]);
const playlistID = ref(-1)
const hoverIndex = ref(-1);

const playTrack = (track) => {
  player.setTrack(track)
  player.play()
};

const toggleLike = (track) => {
  track.isLiked = !track.isLiked
  // Здесь будет вызов API для обновления статуса лайка
};

const hideErrorImage = (e) => {
  e.target.style.display = 'none'
};

const formatDate = (dateString) => {
            if (!dateString) return 'Date not available';

            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            });
        };

const player = usePlayerStore();

onMounted(async () => {
  try {
    var userID = getUserID(localStorage.getItem("token"));
    playlistID.value = await getFavPlaylistID(userID);
    tracks.value = await getTracksByQuery({
      playlist_id: playlistID.value
    }, true);
  } catch (error) {
    console.error("Ошибка при загрузке данных:", error);
  }
});

</script>

<template>
  <MainHeader />
  <main>
    <section class="section liked-section">
      <div class="section-header">
        <h2>Liked Songs</h2>
        <div class="subheader">Your favorite tracks</div>
      </div>

      <div class="enhanced-table">
        <div class="table-header">
          <div class="header-cell" style="width: 5%">#</div>
          <div class="header-cell">Title</div>
          <div class="header-cell">Album</div>
          <div class="header-cell">Added</div>
          <div class="header-cell"><span class="icon icon-time"></span></div>
        </div>

        <div class="table-row" v-for="(track, index) in tracks" :key="track.id" @click="playTrack(track)"
          @mouseenter="hoverIndex = index" @mouseleave="hoverIndex = -1">
          <div class="table-cell track-number">
            <transition name="fade" mode="out-in">
              <span v-if="hoverIndex !== index" class="number">{{ index + 1 }}</span>
              <button v-else class="btn-play-row">
                <span class="icon icon-play-white"></span>
              </button>
            </transition>
          </div>

          <div class="table-cell track-info">
            <div class="cover-sm">
              <img v-if="track.coverUrl" :src="track.coverUrl" @error="hideErrorImage" />
              <div v-else class="cover-placeholder">🎵</div>
            </div>
            <div class="track-text">
              <h3>{{ track.name }}</h3>
              <p>{{ track.artist.name }}</p>
            </div>
          </div>

          <div class="table-cell">
            <span class="album-name">{{ "album" }}</span>
          </div>

          <div class="table-cell">
            <span class="date-added">{{ formatDate(track.created_at) }}</span>
          </div>

          <div class="table-cell">
            <div class="duration-container">
              <!-- <span class="duration">{{ "Dur" }}</span> -->
              <button class="btn-like" @click.stop="toggleLike(track)">
                <span :class="['icon', 'icon-like', { liked: track.isLiked }]"></span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>
  </main>
</template>


<style scoped>
.liked-section {
  padding: 2rem;
  max-width: 1200px;
  margin: 0 auto;
}

.section-header {
  margin-bottom: 2rem;
}

.section-header h2 {
  font-size: 2rem;
  color: white;
  margin: 0;
}

.subheader {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.enhanced-table {
  display: flex;
  flex-direction: column;
  background: rgba(24, 24, 24, 0.7);
  border-radius: 12px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

/* .table-header {
  display: grid;
  grid-template-columns: 50px 2fr 1fr 1fr 100px;
  padding: 1rem;
  gap: 15px;
} */

.table-header {
  display: grid;
  grid-template-columns: 50px 2fr 1fr 1fr 100px;
  padding: 1rem;
  background: rgba(40, 40, 40, 0.9);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
  text-transform: uppercase;
  letter-spacing: 1px;
}
/* .table-row {
  display: grid;
  grid-template-columns: 50px 2fr 1fr 1fr 100px;
  align-items: center;
  padding: 0.8rem 1rem;
  gap: 15px;
} */

.table-row {
  display: grid;
  grid-template-columns: 50px 2fr 1fr 1fr 100px;
  align-items: center;
  padding: 0.8rem 1rem;
  transition: all 0.3s ease;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}


.header-cell {
  padding: 0 1rem;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateX(5px);
}

.table-cell {
  padding: 0 1rem;
  color: white;
}

.track-number {
  width: 5%;
  position: relative;
  color: rgba(255, 255, 255, 0.7);
}

.btn-play-row {
  background: #E50914;
  border: none;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-play-row:hover {
  transform: scale(1.1);
  background: #ff1a1a;
}

.icon-play-white {
  display: inline-block;
  width: 12px;
  height: 12px;
  background-color: white;
  mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M8 5v14l11-7z'/%3E%3C/svg%3E") no-repeat center;
}

.track-info {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 1rem;
  min-width: 0;
}

.cover-sm {
  width: 40px;
  height: 40px;
  border-radius: 4px;
  overflow: hidden;
  background: linear-gradient(135deg, #2b2b2b 0%, #1a1a1a 100%);
  flex-shrink: 0;
}

.cover-sm img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cover-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
}

.track-text {
  min-width: 0;
}

.track-text h3 {
  margin: 0;
  font-size: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-text p {
  margin: 0.2rem 0 0;
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.7);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.album-name {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.date-added {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.duration-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.duration {
  color: rgba(255, 255, 255, 0.7);
  font-size: 0.9rem;
}

.btn-like {
  background: none;
  border: none;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  opacity: 0;
  transition: all 0.2s ease;
}

.table-row:hover .btn-like {
  opacity: 1;
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

.icon-like.liked {
  filter: brightness(0) saturate(100%) invert(27%) sepia(89%) saturate(3733%) hue-rotate(347deg) brightness(90%) contrast(97%);
  opacity: 1;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>