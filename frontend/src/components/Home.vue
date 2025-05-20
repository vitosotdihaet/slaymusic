<template>

  <body>
    <MainHeader />

    <main>
      <section class="section">
        <h2>Liked Songs</h2>
        <div class="card-row">
          <div class="card">
            <div class="cover">
              #
              <button class="btn-play">
                <span class="icon icon-play-white"></span>
              </button>
            </div>
            <div class="info">
              <div class="info-row">
                <h3>Discover Weekly</h3>
                <div class="card-actions">
                </div>
              </div>
              <p>Weekly mix</p>
            </div>
          </div>
          <div class="card">
            <div class="cover">
              #
              <button class="btn-play">
                <span class="icon icon-play-white"></span>
              </button>
            </div>
            <div class="info">
              <div class="info-row">
                <h3>Discover Weekly</h3>
                <div class="card-actions">
                </div>
              </div>
              <p>Weekly mix</p>
            </div>
          </div>
          <div class="card">
            <div class="cover">
              #
              <button class="btn-play">
                <span class="icon icon-play-white"></span>
              </button>
            </div>
            <div class="info">
              <div class="info-row">
                <h3>Discover Weekly</h3>
                <div class="card-actions">
                </div>
              </div>
              <p>Weekly mix</p>
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

<script>
import MainHeader from '@/components/Header.vue'
export default {
  components: {
    MainHeader,
  },
};
</script>