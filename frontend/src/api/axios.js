import axios from 'axios';

// Use relative API URL in production (through nginx proxy),
// with optional override via Vite env for local/dev scenarios.
const axiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/',
});

// Interceptor to attach the JWT Authorization header if it exists
axiosInstance.interceptors.request.use(
  (config) => {
    const token = window.localStorage.getItem('hardware-hub-token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

export default axiosInstance;
