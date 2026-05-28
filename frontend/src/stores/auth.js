import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import axios from '../api/axios';

function decodeToken(jwtToken) {
  try {
    const base64Url = jwtToken.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const decoded = JSON.parse(jsonPayload);
    return {
      id: 1, // Set a default ID for front-end structure compatibility
      username: decoded.sub,
      isAdmin: decoded.is_admin,
      displayName: decoded.sub, // Use username as display name
    };
  } catch (err) {
    console.error('Failed to decode JWT token', err);
    throw err;
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(window.localStorage.getItem('hardware-hub-token') || '');
  const currentUser = ref(null);

  // Restore session from localStorage if token exists
  if (token.value) {
    try {
      currentUser.value = decodeToken(token.value);
    } catch {
      token.value = '';
      window.localStorage.removeItem('hardware-hub-token');
    }
  }

  const isAuthenticated = computed(() => Boolean(token.value));
  const session = computed(() => currentUser.value);

  async function login(username, password) {
    try {
      const response = await axios.post('/api/v1/auth/login', {
        username: username.trim(),
        password: password,
      });

      const accessToken = response.data.access_token;
      token.value = accessToken;
      window.localStorage.setItem('hardware-hub-token', accessToken);

      const user = decodeToken(accessToken);
      currentUser.value = user;
      return user;
    } catch (err) {
      const detail = err.response?.data?.detail || 'Invalid credentials or connection error.';
      throw new Error(detail);
    }
  }

  function logout() {
    token.value = '';
    currentUser.value = null;
    window.localStorage.removeItem('hardware-hub-token');
  }

  return {
    token,
    session,
    currentUser,
    isAuthenticated,
    login,
    logout,
    userDirectory: [], // Kept as empty array for API backwards-compatibility
  };
});
