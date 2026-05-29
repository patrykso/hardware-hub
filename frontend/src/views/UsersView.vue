<template>
  <AppShell>
    <div class="toolbar-grid narrow">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input
          v-model="userQuery"
          type="search"
          placeholder="Search users..."
        />
      </label>

      <button
        class="primary-button small"
        type="button"
        @click="openAddUserModal"
      >
        <span class="material-symbols-outlined">person_add</span>
        Add User
      </button>
    </div>

    <section class="surface-card">
      <div class="table-shell desktop-only">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Role</th>
              <th>Created</th>
              <th class="align-right">Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>
                <strong>{{ user.username }}</strong>
              </td>
              <td>
                <span
                  class="status-badge"
                  :class="user.is_admin ? 'repair' : 'available'"
                >
                  {{ user.is_admin ? "Admin" : "User" }}
                </span>
              </td>
              <td class="cell-sub">
                {{ hub.formatDateTime(user.created_at) }}
              </td>
              <td class="actions-cell align-right">
                <button
                  v-if="user.id !== hub.currentUser.value?.id"
                  class="icon-button danger"
                  type="button"
                  title="Delete User"
                  @click="confirmDeleteUser(user)"
                >
                  <span class="material-symbols-outlined">delete</span>
                </button>
                <span v-else class="cell-sub">(You)</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <ConfirmDialog
      :visible="userDeleteDialog.visible"
      title="Delete User"
      :message="`Delete user '${userDeleteDialog.user?.username || ''}'? This cannot be undone.`"
      confirm-label="Delete"
      variant="danger"
      icon="delete"
      @confirm="executeDeleteUser"
      @cancel="userDeleteDialog.visible = false"
    />

    <Teleport to="body">
      <Transition name="dialog-fade">
        <div
          v-if="userModal.visible"
          class="dialog-overlay"
          @click.self="userModal.visible = false"
        >
          <div
            class="dialog-card dialog-form-card"
            role="dialog"
            aria-modal="true"
          >
            <h3 class="dialog-title">Create User</h3>
            <form class="edit-form" @submit.prevent="executeCreateUser">
              <label>
                <span>Username</span>
                <input
                  v-model="userModal.username"
                  type="text"
                  required
                  placeholder="jsmith"
                />
              </label>
              <label>
                <span>Password</span>
                <input
                  v-model="userModal.password"
                  type="password"
                  required
                  placeholder="••••••••"
                />
              </label>
              <label class="checkbox-label">
                <input v-model="userModal.isAdmin" type="checkbox" />
                <span>Administrator</span>
              </label>
              <div class="dialog-actions">
                <button
                  class="ghost-button"
                  type="button"
                  @click="userModal.visible = false"
                >
                  Cancel
                </button>
                <button class="primary-button" type="submit">Create</button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>
  </AppShell>
</template>

<script setup>
import { computed, reactive, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import { useHubState } from "../data/hubState";

const hub = useHubState();
const userQuery = ref("");

const userModal = reactive({
  visible: false,
  username: "",
  password: "",
  isAdmin: false,
});
const userDeleteDialog = reactive({ visible: false, user: null });

const filteredUsers = computed(() => {
  if (!hub.userDirectory.value) return [];
  return hub.userDirectory.value
    .filter((u) =>
      u.username.toLowerCase().includes(userQuery.value.toLowerCase()),
    )
    .sort((a, b) => a.username.localeCompare(b.username));
});

function openAddUserModal() {
  userModal.username = "";
  userModal.password = "";
  userModal.isAdmin = false;
  userModal.visible = true;
}

async function executeCreateUser() {
  try {
    await hub.createUser({
      username: userModal.username.trim(),
      password: userModal.password,
      is_admin: userModal.isAdmin,
    });
    userModal.visible = false;
  } catch (e) {
    window.alert(e instanceof Error ? e.message : "Failed to create user.");
  }
}

function confirmDeleteUser(user) {
  userDeleteDialog.user = user;
  userDeleteDialog.visible = true;
}

async function executeDeleteUser() {
  if (!userDeleteDialog.user) return;
  try {
    await hub.deleteUser(userDeleteDialog.user.id);
  } catch (e) {
    window.alert(e instanceof Error ? e.message : "Failed to delete user.");
  }
  userDeleteDialog.visible = false;
  userDeleteDialog.user = null;
}
</script>
