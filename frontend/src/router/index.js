import { createRouter, createWebHistory } from 'vue-router'

import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import Home from '../components/Home.vue'
import Profile from '../components/Profile.vue'
import NotFound from '../components/NotFound.vue'
import Liked from '../components/Liked.vue'

import { jwtDecode } from 'jwt-decode'
import UploadTrack from '../components/UploadTrack.vue'
import apiClient, { BackendURL } from '../api/axios'
import { ref } from 'vue'

const routes = [
  {
    path: '/login',
    component: Login,
    meta: {
      requiresAuth: false,
      player: false,
    }
  },
  {
    path: '/register',
    component: Register,
    meta: {
      requiresAuth: false,
      player: false,
    }
  },
  {
    path: '/',
    component: Home,
    meta: {
      requiresAuth: true,
      player: true,
    }
  },
  {
    path: '/home',
    component: Home,
    meta: {
      requiresAuth: true,
      player: true,
    }
  },
  {
    path: '/profile',
    component: Profile,
    meta: {
      requiresAuth: true,
      player: true,
    }
  },
  {
    path: '/liked',
    component: Liked,
    meta: {
      requiresAuth: true,
      player: true,
    }
  },
  {
    path: '/upload',
    component: UploadTrack,
    meta: {
      requiresAuth: true,
      player: false,
    }
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    meta: {
      requiresAuth: false,
      player: false,
    }
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export function isTokenValid(token) {
  try {
    const decoded = jwtDecode(token);
    console.log("success decode: ", decoded);
    return decoded.exp * 1000 > Date.now();
  } catch (err) {
    console.log("token error", err);
    return false;
  }
}

export function getUserID(token) {
  try {
    const decoded = jwtDecode(token);
    console.log("getUserID: success decode: ", decoded);
    return decoded.id;
  } catch (err) {
    console.log("getUserID: token error", err);
    return false;
  }
}

export async function getArtistByID(artist_id) {
  try {
    const response = await apiClient.get(`/user/artist/?id=${artist_id}`, {}, {});
    return response.data;
  } catch (error) {
    console.log("artist error", error);
  }
  return {};
}

export async function getTracksByQuery(query, isLiked = false) {
  var tracks = ref([]);
  const tracksResponse = await apiClient.get(`/tracks/`, {
    params: query
  });

  tracks.value = tracksResponse.data.map(track => ({
    ...track,
    artist: null,
    audioUrl: null,
    coverUrl: null,
    isLiked: isLiked,
  }));

  for (let i = 0; i < tracks.value.length; i++) {
    try {
      tracks.value[i].artist = await getArtistByID(tracks.value[i].artist_id);
    } catch (error) {
      tracks.value[i].artist = { name: 'Unknown Artist' };
    }
    try {
      tracks.value[i].audioUrl = `track/stream/?id=${tracks.value[i].id}`;
    } catch (error) {
      tracks.value[i].audioUrl = '';
    }
    try {
      tracks.value[i].coverUrl = BackendURL(`track/image/?id=${tracks.value[i].id}`);
    } catch (error) {
      tracks.value[i].coverUrl = ``;
    }
    tracks.value[i].isLiked = isLiked;
  }
  console.log("GET TRACKS", tracks.value);
  return tracks.value;
};

export async function getFavPlaylistID(user_id) {
  var playlists = ref([]);
  const playlistsResponse = await apiClient.get(`/playlists/?author_id=${user_id}`, {}, {});
  playlists.value = playlistsResponse.data;
  console.log("playlist->> ", playlistsResponse.data);
  var playlist_fav_id = -1;
  playlists.value.forEach(element => {
    if (element.name == "fav") {
      playlist_fav_id = element.id;
      return;
    }
  });
  return playlist_fav_id;
}

export async function likeTrack(track_id, user_id) {
  var playlistID = await getFavPlaylistID(user_id);
  if (playlistID == -1) {
    console.log(`Error while like track ${track_id} with user ${user_id}`);
    return;
  }
  var response = await apiClient.post("/playlist/track/", {}, {
    params: {
      playlist_id: playlistID,
      track_id: track_id
    }
  });
  console.log("like response ->", response);
}

export async function unlikeTrack(track_id, user_id) {
  var playlistID = await getFavPlaylistID(user_id);
  if (playlistID == -1) {
    console.log(`Error while unlike track ${track_id} with user ${user_id}`);
    return;
  }
  var response = await apiClient.delete(`/playlist/track/?playlist_id=${playlistID}&track_id=${track_id}`, {}, {});
  console.log("unlike response ->", response);
}

export async function isLiked(track_id, user_id) {
  try {
    var playlistID = await getFavPlaylistID(user_id);
    if (playlistID == -1) {
      console.log(`Error while unlike track ${track_id} with user ${user_id}`);
      return false;
    }
    var tracks = await getTracksByQuery({
      playlist_id: playlistID,
    });
    var exist = false;
    tracks.forEach(track => {
      if (track.id == track_id) {
        exist = true;
        return true;
      }
    });
    return exist;
  } catch (error) {
    console.log("error while check liked: ", error);
  }
  return false;
}

router.beforeEach((to, from, next) => {
  document.title = 'Slay Music';
  const isAuthRequired = to.matched.some(route => route.meta.requiresAuth);
  const token = localStorage.getItem('token');

  if (isAuthRequired && !isTokenValid(token)) {
    next('/login');
  } else if (to.path === '/login' && isTokenValid(token)) {
    next('/');
  } else {
    next();
  }
});

export default router
