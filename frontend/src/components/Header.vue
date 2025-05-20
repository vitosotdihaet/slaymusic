<template>
    <header>
        <div class="left-group">
            <div class="logo">
                <span class="icon icon-logo"></span>Slay
            </div>
            <nav class="main-nav">
                <router-link to="/" exact-active-class="active">
                    <span class="icon icon-home"></span>
                    Home
                </router-link>
                <router-link to="/playlists" active-class="active">
                    <span class="icon icon-playlists"></span>
                    Playlists
                </router-link>
                <router-link to="/liked" active-class="active">
                    <span class="icon icon-liked"></span>
                    Liked
                </router-link>
                <router-link to="/profile" active-class="active">
                    <span class="icon icon-user"></span>
                    Profile
                </router-link>
            </nav>
        </div>
        <div class="right-group">
            <router-link to="#search">
                <span class="icon icon-search"></span>
            </router-link>
        </div>
    </header>
</template>

<style>
@import '../assets/css/styles.css';
</style>