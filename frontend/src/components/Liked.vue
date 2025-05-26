<template>
    <MainHeader />
    <main>
        <section class="section liked-section">
            <h2>Liked Songs</h2>
            <table class="track-table">
                <thead>
                    <tr>
                        <th width="5%">#</th>
                        <th>Title</th>
                        <th>Album</th>
                        <th>Date added</th>
                        <th><span class="icon icon-time"></span></th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="track-number">
                            <span class="number">1</span>
                            <button class="btn-play-row">
                                <span class="icon icon-play-white"></span>
                            </button>
                        </td>
                        <td class="track-info">
                            <div class="cover-sm">🎵</div>
                            <div>
                                <h3>First Song</h3>
                                <p>First Artist</p>
                            </div>
                        </td>
                        <td>First Album</td>
                        <td>May 10, 2025</td>
                        <td>3:42</td>
                    </tr>
                    <tr>
                        <td class="track-number">
                            <span class="number">2</span>
                            <button class="btn-play-row">
                                <span class="icon icon-play-white"></span>
                            </button>
                        </td>
                        <td class="track-info">
                            <div class="cover-sm">🎵</div>
                            <div>
                                <h3>Second Song</h3>
                                <p>Another Artist</p>
                            </div>
                        </td>
                        <td>Another Album</td>
                        <td>May 10, 2025</td>
                        <td>4:05</td>
                    </tr>
                    <tr>
                        <td class="track-number">
                            <span class="number">3</span>
                            <button class="btn-play-row">
                                <span class="icon icon-play-white"></span>
                            </button>
                        </td>
                        <td class="track-info">
                            <div class="cover-sm">🎵</div>
                            <div>
                                <h3>Chill Vibes</h3>
                                <p>Cool Band</p>
                            </div>
                        </td>
                        <td>Chill Album</td>
                        <td>May 9, 2025</td>
                        <td>2:58</td>
                    </tr>
                </tbody>
            </table>
        </section>
    </main>
</template>

<script>
import MainHeader from '@/components/Header.vue'
export default {
    components: {
        MainHeader,
    },
};
</script>

<style>

.track-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  color: #fff;
  font-size: 0.95rem;
}

.track-table thead {
  border-bottom: 1px solid #444;
}

.track-table th,
.track-table td {
  padding: 0.75rem 1rem;
  text-align: left;
}

.track-table tbody tr {
  transition: background 0.2s ease;
}

.track-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.track-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.cover-sm {
  width: 40px;
  height: 40px;
  background-color: #333;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 4px;
  font-size: 0.8rem;
  flex-shrink: 0;
}

.track-number {
  position: relative;
  width: 24px;
}

.track-number .number {
  display: inline-block;
}

.track-number .btn-play-row {
  display: none;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
}

.track-number .icon-play {
  width: 16px;
  height: 16px;
  background-color: white;
  mask: url('../assets/css/icons/play-white.png') no-repeat center;
  -webkit-mask: url('../assets/css/icons/play-white.png') no-repeat center;
  mask-size: cover;
  -webkit-mask-size: cover;
}

.track-table tbody tr:hover .track-number .number {
  display: none;
}

.track-table tbody tr:hover .track-number .btn-play-row {
  display: inline-block;
}
</style>