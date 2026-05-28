import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

const SESSION_KEY = 'hardware-hub-session';

const userDirectory = [
  { id: 1, username: 'admin', password: 'admin', displayName: 'Alex Morgan', isAdmin: true },
  { id: 2, username: 'user', password: 'user', displayName: 'Jordan Lee', isAdmin: false },
];

export const useAuthStore = defineStore('auth', () => {
  const session = ref(readSession());

  function readSession() {
    if (typeof window === 'undefined') {
      return null;
    }

    try {
      const stored = window.localStorage.getItem(SESSION_KEY);
      return stored ? JSON.parse(stored) : null;
    } catch {
      return null;
    }
  }

  function persistSession(value) {
    if (typeof window === 'undefined') {
      return;
    }

    if (value) {
      window.localStorage.setItem(SESSION_KEY, JSON.stringify(value));
    } else {
      window.localStorage.removeItem(SESSION_KEY);
    }
  }

  function login(username, password) {
    const user = userDirectory.find(
      (entry) => entry.username.toLowerCase() === username.trim().toLowerCase() && entry.password === password
    );

    if (!user) {
      throw new Error('Invalid credentials. Use admin / admin or user / user.');
    }

    const payload = {
      id: user.id,
      username: user.username,
      displayName: user.displayName,
      isAdmin: user.isAdmin,
    };

    session.value = payload;
    persistSession(payload);
    return payload;
  }

  function logout() {
    session.value = null;
    persistSession(null);
  }

  const currentUser = computed(() => {
    if (!session.value) {
      return null;
    }
    return session.value;
  });

  const isAuthenticated = computed(() => Boolean(currentUser.value));

  return {
    session,
    currentUser,
    isAuthenticated,
    login,
    logout,
    userDirectory,
  };
});
