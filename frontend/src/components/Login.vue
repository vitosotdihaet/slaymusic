<template>

  <body>
    <div class="login-container">
      <div class="login-box">
        <div class="login-logo">
          <span class="icon icon-logo"></span><span>Slay</span>
        </div>

        <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>

        <form class="login-form" @submit.prevent="handleRegister">
          <label for="username">Username</label>
          <input type="text" id="username" v-model="form.username" required />

          <label for="password">Password</label>
          <input type="password" id="password" v-model="form.password" required />

          <button type="submit">Login</button>
        </form>
        <div class="register-link">
          <a href="/register">Don't have an account? Register</a>
        </div>
      </div>
    </div>
  </body>
</template>

<script>
import apiClient from '@/api/axios';

export default {
  data() {
    return {
      form: {
        username: '',
        password: '',
      },
      errorMessage: ''
    }
  },
  methods: {
    async login(username, password) {
      return apiClient.post('/user/login', {
        username: username,
        password: password,
      });
    },
    async handleRegister() {
      try {
        const { name, username, password, password_repeat } = this.form;

        const result = await this.login(username, password);

        if (result.status != 200) {
          this.errorMessage = result.data.detail;
          return;
        }

        localStorage.setItem("token", result.data.token);
        this.$router.push(result.data.next);
      } catch (error) {
        if (error.response && error.response.data && error.response.data.detail) {
          this.errorMessage = error.response.data.detail;
        } else {
          this.errorMessage = "Something went wrong.";
        }
      }
    },
  },
}
</script>

<style>
@import '../assets/css/styles.css';
@import '../assets/css/login.css';
</style>
