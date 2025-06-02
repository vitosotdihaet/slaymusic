<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-logo">
        <span class="icon icon-logo"></span><span>Slay</span>
      </div>

      <div class="error-message" v-if="errorMessage">{{ errorMessage }}</div>

      <form class="login-form" @submit.prevent="handleRegister">
        <label for="name">Name</label>
        <input type="text" id="name" v-model="form.name" required />

        <label for="username">Username</label>
        <input type="text" id="username" v-model="form.username" required />

        <label for="password">Password</label>
        <input type="password" id="password" v-model="form.password" required />

        <label for="password">Repeat password</label>
        <input type="password" id="password_repeat" v-model="form.password_repeat" required />

        <button type="submit">Register</button>
      </form>

      <div class="register-link">
        <router-link to="/login">Already have an account? Login</router-link>
      </div>
    </div>
  </div>
</template>

<script>
import apiClient from '@/api/axios';

export default {
  data() {
    return {
      form: {
        name: '',
        username: '',
        password: '',
        password_repeat: '',
      },
      errorMessage: ''
    }
  },
  methods: {
    async createUser(name, username, password) {
      return apiClient.post('/user/register', {
        name: name,
        username: username,
        password: password,
      });
    },
    async handleRegister() {
      try {
        const { name, username, password, password_repeat } = this.form;

        if (password !== password_repeat) {
          this.errorMessage = "Passwords do not match.";
          return;
        }

        const result = await this.createUser(name, username, password);

        if (result.status != 201) {
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
