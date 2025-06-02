import axios from 'axios';
import router from '@/router';

export function BackendURL(suff) {
  return `${process.env.VUE_APP_BACKEND_URL}${suff}`;
}

const apiClient = axios.create({
  baseURL: process.env.VUE_APP_BACKEND_URL,
});

apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      router.push('/login');
    }
    return Promise.reject(error);
  }
);

export default apiClient;
