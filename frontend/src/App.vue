<template>
  <Layout />
</template>

<script>
import Layout from '@/components/Layout.vue';
export default {
  components: {
    Layout,
  },
  mounted() {
      console.log('Backend URL:', process.env.VUE_APP_BACKEND_URL);
  },
};
</script>

<style>
@import '@/assets/css/styles.css';
</style>