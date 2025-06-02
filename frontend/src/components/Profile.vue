<template>
    <MainHeader />
    <main>
        <section class="section profile-section">
            <div class="profile-header">
                <div class="avatar-wrapper">
                    <img src="slayrock.png" alt="User Avatar" class="avatar-img" />
                    <button class="btn-change-avatar">✏️</button>
                </div>
                <div class="user-info">
                    <h2>{{ user.username }}</h2>
                    <p> {{ user.name }} </p>
                    <p>Member since: {{ formatDate(user.created_at) }}</p>
                </div>
            </div>

            <!-- <form class="form password-form">
                <h3>Change Password</h3>
                <label>
                    Current Password
                    <input type="password" name="current-password" required />
                </label>
                <label>
                    New Password
                    <input type="password" name="new-password" required />
                </label>
                <label>
                    Confirm New Password
                    <input type="password" name="confirm-password" required />
                </label>
                <button type="submit" class="btn-save">Update Password</button>
            </form> -->

            <button class="btn-delete">Delete Account</button>
            <button class="btn-delete" @click="logout" style="margin-left: 10px;">Log out</button>

        </section>
    </main>
</template>

<script>
import MainHeader from '@/components/Header.vue'
import apiClient from '../api/axios';
export default {
    components: {
        MainHeader,
    },
    data() {
        return {
            user: {
                username: '',
                name: '',
                created_at: '',
            },
        }
    },
    methods: {
        logout() {
            localStorage.removeItem("token");
            this.$router.push("/login");
        },
        async fetchUserData() {
            try {
                const response = await apiClient.get('/user/');
                console.log(response.data);
                this.user = response.data;
            } catch (error) {
                console.error('Error profile load', error);
            }
        },
        formatDate(dateString) {
            if (!dateString) return 'Date not available';

            const date = new Date(dateString);
            return date.toLocaleDateString('en-US', {
                month: 'short',
                day: 'numeric'
            });
        }
    },
    mounted() {
        this.fetchUserData()
    }
};
</script>

<style>
.profile-section {
  color: #fff;
  max-width: 600px;
  margin: 2rem auto;
  padding: 1rem;
}

.profile-header {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-bottom: 2rem;
}

.avatar-wrapper {
  position: relative;
  width: 100px;
  height: 100px;
}

.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  border-radius: 50%;
  border: 2px solid #555;
}

.btn-change-avatar {
  position: absolute;
  bottom: 0;
  right: 0;
  background: #E50914;
  border: none;
  border-radius: 50%;
  color: #000;
  font-size: 0.75rem;
  padding: 0.4rem;
  cursor: pointer;
  transition: background 0.2s ease;
  border: 2px solid #555;
}

.btn-change-avatar:hover {
  background: #9a060d;
}

.user-info h2 {
  font-size: 1.5rem;
  margin: 0;
}

.user-info p {
  margin: 0.2rem 0;
  color: #aaa;
}

.form.password-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background-color: rgba(255, 255, 255, 0.05);
  padding: 1rem;
  border-radius: 8px;
}

.password-form h3 {
  margin-bottom: 0.5rem;
}

.password-form label {
  display: flex;
  flex-direction: column;
  font-size: 0.9rem;
}

.password-form input {
  margin-top: 0.3rem;
  padding: 0.5rem;
  border: none;
  border-radius: 4px;
  background: #222;
  color: white;
}

.btn-save {
  background: #E50914;
  color: black;
  padding: 0.6rem 1.2rem;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  align-self: flex-start;
}

.btn-save:hover {
  background: #9a060d;
}

.btn-delete {
  margin-top: 2rem;
  background: transparent;
  color: #f55;
  border: 1px solid #f55;
  padding: 0.6rem 1.2rem;
  border-radius: 20px;
  cursor: pointer;
}

.btn-delete:hover {
  background: rgba(255, 85, 85, 0.1);
}
</style>