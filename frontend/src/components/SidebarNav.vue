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
        :class="{ active: isActive(item) }"
      >
        <span
          class="material-symbols-outlined"
          :class="{ filled: isActive(item) }"
          >{{ item.icon }}</span
        >
        <span>{{ item.label }}</span>
      </router-link>
    </nav>

    <div class="sidebar-footer">
      <button
        v-if="isAdmin"
        class="sidebar-link danger"
        type="button"
        @click="handleResetDatabase"
      >
        <span class="material-symbols-outlined">restart_alt</span>
        <span>Reset Database</span>
      </button>
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
      :class="{ active: isActive(item) }"
    >
      <span
        class="material-symbols-outlined"
        :class="{ filled: isActive(item) }"
        >{{ item.icon }}</span
      >
      <span>{{ item.label }}</span>
    </router-link>
  </nav>

  <ConfirmDialog
    :visible="resetDialog.visible"
    title="Reset Database"
    message="Do you want to reset the database and seed it with initial data?"
    confirm-label="Reset"
    variant="danger"
    icon="restart_alt"
    @confirm="executeResetDatabase"
    @cancel="resetDialog.visible = false"
  />
</template>

<script setup>
import { computed, reactive } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useHubState } from "../data/hubState";
import { useThemeStore } from "../stores/theme";
import ConfirmDialog from "./ConfirmDialog.vue";

const route = useRoute();
const router = useRouter();
const hub = useHubState();
const themeStore = useThemeStore();

const isAdmin = computed(() => !!hub.currentUser.value?.isAdmin);
const resetDialog = reactive({ visible: false });

function handleResetDatabase() {
  resetDialog.visible = true;
}

async function executeResetDatabase() {
  resetDialog.visible = false;
  try {
    await hub.resetDatabase();
    window.alert("Database reset completed successfully.");
  } catch (err) {
    window.alert(err instanceof Error ? err.message : "Failed to reset database.");
  }
}

function isActive(item) {
  if (item.match === "/admin") {
    return route.path === "/admin" || route.path.startsWith("/admin/equipment/");
  }
  return route.path.startsWith(item.match);
}

const allItems = [
  { label: "Hardware", to: "/hardware", match: "/hardware", icon: "devices" },
  { label: "My Rentals", to: "/rentals", match: "/rentals", icon: "assignment" },
  {
    label: "All Rentals",
    to: "/admin/rentals",
    match: "/admin/rentals",
    icon: "history_edu",
    adminOnly: true,
  },
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
