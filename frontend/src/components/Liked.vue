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