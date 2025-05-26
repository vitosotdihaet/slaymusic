import { createRouter, createWebHistory } from 'vue-router'

import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import Home from '../components/Home.vue'
import Profile from '../components/Profile.vue'
import NotFound from '../components/NotFound.vue'
import Liked from '../components/Liked.vue'

import { jwtDecode } from 'jwt-decode';
import UploadTrack from '../components/UploadTrack.vue'

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

router.beforeEach((to, from, next) => {
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
