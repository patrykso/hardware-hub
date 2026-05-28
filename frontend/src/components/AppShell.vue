<template>
  <div class="app-shell">
    <SidebarNav />

    <div class="shell-main">
      <header v-if="showTopBar" class="shell-topbar">
        <div>
          <p class="eyebrow">Hardware Rental Hub</p>
          <h1>{{ pageTitle }}</h1>
        </div>

        <div class="shell-user" v-if="currentUser">
          <div class="avatar">{{ initials }}</div>
          <div>
            <strong>{{ currentUser.displayName }}</strong>
            <span>{{ currentUser.isAdmin ? 'Admin' : 'User' }}</span>
          </div>
        </div>
      </header>

      <main class="shell-content">
        <slot />
      </main>
    </div>

    <button v-if="showFab" class="assistant-fab" type="button" @click="$router.push('/audit')" title="Open AI audit">
      <span class="material-symbols-outlined filled">smart_toy</span>
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import SidebarNav from './SidebarNav.vue';
import { useHubState } from '../data/hubState';

defineProps({
  showTopBar: {
    type: Boolean,
    default: true,
  },
  showFab: {
    type: Boolean,
    default: true,
  },
});

const hub = useHubState();
const route = useRoute();

const pageTitle = computed(() => route.meta.title || 'Hardware Rental Hub');
const currentUser = computed(() => hub.currentUser.value);
const initials = computed(() => {
  const name = currentUser.value?.displayName || 'User';
  return name
    .split(' ')
    .map((part) => part[0])
    .join('')
    .slice(0, 2)
    .toUpperCase();
});
</script>
