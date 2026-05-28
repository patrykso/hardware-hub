import axios from 'axios';

// Centralized Axios configuration pointing to backend server
const axiosInstance = axios.create({
  baseURL: 'http://localhost:8000',
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
