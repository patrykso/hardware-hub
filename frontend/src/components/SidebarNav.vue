<template>
  <aside class="sidebar">
    <div class="sidebar-brand">
      <div class="brand-mark">
        <span class="material-symbols-outlined filled">deployed_code</span>
      </div>
      <div>
        <strong>Hardware Hub</strong>
      </div>
    </div>

    <nav class="sidebar-nav">
      <router-link
        v-for="item in items"
        :key="item.to"
        :to="item.to"
        class="sidebar-link"
        :class="{ active: route.path.startsWith(item.match) }"
      >
        <span
          class="material-symbols-outlined"
          :class="{ filled: route.path.startsWith(item.match) }"
          >{{ item.icon }}</span
        >
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button
        class="sidebar-link theme-toggle"
        type="button"
        @click="themeStore.toggle()"
      >
        <span class="material-symbols-outlined">{{
          themeStore.isDark ? "light_mode" : "dark_mode"
        }}</span>
        <span>{{ themeStore.isDark ? "Light Mode" : "Dark Mode" }}</span>
      </button>
      <button class="sidebar-link danger" type="button" @click="logout">
        <span class="material-symbols-outlined">logout</span>
        <span>Logout</span>
      </button>
    </div>
  </aside>

  <nav class="mobile-nav">
    <router-link
      v-for="item in items"
      :key="item.to"
      :to="item.to"
      class="mobile-nav-item"
      :class="{ active: route.path.startsWith(item.match) }"
    >
      <span
        class="material-symbols-outlined"
        :class="{ filled: route.path.startsWith(item.match) }"
        >{{ item.icon }}</span
      >
      <span>{{ item.label }}</span>
    </router-link>
  </nav>
</template>

<script setup>
import { computed } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useHubState } from "../data/hubState";
import { useThemeStore } from "../stores/theme";

const route = useRoute();
const router = useRouter();
const hub = useHubState();
const themeStore = useThemeStore();

const allItems = [
  { label: "Hardware", to: "/hardware", match: "/hardware", icon: "devices" },
  { label: "Rentals", to: "/rentals", match: "/rentals", icon: "assignment" },
  {
    label: "Admin",
    to: "/admin",
    match: "/admin",
    icon: "admin_panel_settings",
    adminOnly: true,
  },
  {
    label: "Users",
    to: "/users",
    match: "/users",
    icon: "group",
    adminOnly: true,
  },
  {
    label: "Audit",
    to: "/audit",
    match: "/audit",
    icon: "smart_toy",
    adminOnly: true,
  },
];

const items = computed(() => {
  const isAdmin = hub.currentUser.value?.isAdmin;
  return allItems.filter((item) => !item.adminOnly || isAdmin);
});

function logout() {
  hub.logout();
  router.push("/login");
}
</script>
