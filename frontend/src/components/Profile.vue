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

            <form class="form password-form">
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
            </form>

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
                const response = await apiClient.get('/accounts/user');
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
