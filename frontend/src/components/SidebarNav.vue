<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-mark">
        <span class="material-symbols-outlined filled">deployed_code</span>
      </div>
      <div>
        <strong>Hardware Manager</strong>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link v-for="item in items" :key="item.to" :to="item.to" class="sidebar-link" :class="{ active: route.path.startsWith(item.match) }">
        <span class="material-symbols-outlined" :class="{ filled: route.path.startsWith(item.match) }">{{ item.icon }}</span>
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button class="sidebar-link danger" type="button" @click="logout">
        <span class="material-symbols-outlined">logout</span>
        <span>Logout</span>
      </button>
    </div>
  </aside>

  <nav class="mobile-nav">
    <router-link v-for="item in items" :key="item.to" :to="item.to" class="mobile-nav-item" :class="{ active: route.path.startsWith(item.match) }">
      <span class="material-symbols-outlined" :class="{ filled: route.path.startsWith(item.match) }">{{ item.icon }}</span>
      <span>{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router';
import { useHubState } from '../data/hubState';

const route = useRoute();
const router = useRouter();
const hub = useHubState();

const items = [
  { label: 'Hardware List', to: '/hardware', match: '/hardware', icon: 'list_alt' },
  { label: 'My Rentals', to: '/rentals', match: '/rentals', icon: 'inventory_2' },
  { label: 'Admin Panel', to: '/admin', match: '/admin', icon: 'admin_panel_settings' },
];

function logout() {
  hub.logout();
  router.push('/login');
}
</script>
