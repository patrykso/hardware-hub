<template>
  <AppShell>
    <div class="tabs-container">
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'equipment' }"
        @click="activeTab = 'equipment'"
      >
        Equipment Inventory
      </button>
      <button
        class="tab-btn"
        :class="{ active: activeTab === 'users' }"
        @click="activeTab = 'users'"
      >
        User Accounts
      </button>
    </div>

    <!-- Equipment Tab content -->
    <div v-if="activeTab === 'equipment'">
      <div class="toolbar-grid">
        <label class="input-group input-search">
          <span class="material-symbols-outlined">search</span>
          <input v-model="query" type="search" placeholder="Search devices..." />
        </label>
        <select v-model="statusFilter" class="input-group input-select">
          <option value="all">All statuses</option>
          <option value="Available">Available</option>
          <option value="In use">In use</option>
          <option value="Repair">Repair</option>
        </select>

        <select v-model="brandFilter" class="input-group input-select">
          <option value="all">All brands</option>
          <option v-for="brand in brands" :key="brand" :value="brand">
            {{ brand }}
          </option>
        </select>

        <select v-model="sortBy" class="input-group input-select">
          <option value="name">Sort by name</option>
          <option value="brand">Sort by brand</option>
        </select>
      </div>

      <section class="surface-card">
        <div class="table-toolbar">
          <span></span>
          <button
            class="primary-button small"
            type="button"
            @click="$router.push('/admin/equipment/new')"
          >
            <span class="material-symbols-outlined">add</span>
            Add Device
          </button>
        </div>

        <div class="table-shell desktop-only">
          <table class="compact-table">
            <thead>
              <tr>
                <th>Device</th>
                <th>Serial</th>
                <th>Status</th>
                <th class="align-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in filteredEquipment" :key="item.id">
                <td>
                  <strong>{{ item.name }}</strong>
                  <span class="cell-sub">{{ item.brand }}</span>
                </td>
                <td class="mono">{{ item.serialNumber }}</td>
                <td>
                  <select
                    class="status-select"
                    :class="statusClass(item.status)"
                    :value="item.status"
                    @change="changeStatus(item.id, $event.target.value)"
                  >
                    <option value="Available">Available</option>
                    <option value="In use">In Use</option>
                    <option value="Repair">Repair</option>
                  </select>
                </td>
                <td class="actions-cell align-right">
                  <router-link
                    class="icon-button"
                    :to="`/admin/equipment/${item.id}`"
                    title="Edit"
                  >
                    <span class="material-symbols-outlined">edit</span>
                  </router-link>
                  <button
                    class="icon-button danger"
                    type="button"
                    title="Delete"
                    @click="confirmDelete(item)"
                  >
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card-list mobile-only">
          <article
            v-for="item in filteredEquipment"
            :key="item.id"
            class="device-card"
          >
            <div>
              <p class="device-card-title">{{ item.name }}</p>
              <p class="device-card-meta">
                {{ item.brand }} · {{ item.serialNumber }}
              </p>
            </div>

            <select
              class="status-select"
              :class="statusClass(item.status)"
              :value="item.status"
              @change="changeStatus(item.id, $event.target.value)"
            >
              <option value="Available">Available</option>
              <option value="In use">In Use</option>
              <option value="Repair">Repair</option>
            </select>

            <div class="card-actions">
              <router-link
                class="ghost-button small"
                :to="`/admin/equipment/${item.id}`"
                >Edit</router-link
              >
              <button
                class="ghost-button small danger"
                type="button"
                @click="confirmDelete(item)"
              >
                Delete
              </button>
            </div>
          </article>
        </div>
      </section>
    </div>

    <!-- Users Tab content -->
    <div v-else-if="activeTab === 'users'">
      <div class="toolbar-grid" style="grid-template-columns: 1fr auto auto;">
        <label class="input-group input-search">
          <span class="material-symbols-outlined">search</span>
          <input v-model="userQuery" type="search" placeholder="Search users..." />
        </label>
        
        <button
          class="primary-button small"
          type="button"
          @click="openAddUserModal"
          style="height: 42px;"
        >
          <span class="material-symbols-outlined">person_add</span>
          Add User
        </button>

        <button
          class="primary-button small danger"
          type="button"
          @click="openResetConfirm"
          style="height: 42px;"
        >
          <span class="material-symbols-outlined">restart_alt</span>
          Reset Database
        </button>
      </div>

      <section class="surface-card" style="margin-top: 24px;">
        <div class="table-shell desktop-only">
          <table class="compact-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Created At</th>
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
                    class="status-select"
                    :class="user.is_admin ? 'status-repair' : 'status-available'"
                    style="padding: 4px 10px; border-radius: 6px; font-weight: 600; font-size: 12px; pointer-events: none;"
                  >
                    {{ user.is_admin ? 'Administrator' : 'Standard User' }}
                  </span>
                </td>
                <td class="cell-sub">{{ hub.formatDateTime(user.created_at) }}</td>
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
                  <span v-else class="cell-sub" style="font-style: italic; padding-right: 8px;">(You)</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="card-list mobile-only">
          <article
            v-for="user in filteredUsers"
            :key="user.id"
            class="device-card"
          >
            <div>
              <p class="device-card-title">{{ user.username }}</p>
              <p class="device-card-meta">
                Role: {{ user.is_admin ? 'Administrator' : 'Standard User' }} · Created: {{ hub.formatDateTime(user.created_at) }}
              </p>
            </div>

            <div class="card-actions">
              <button
                v-if="user.id !== hub.currentUser.value?.id"
                class="ghost-button small danger"
                type="button"
                @click="confirmDeleteUser(user)"
              >
                Delete
              </button>
              <span v-else class="cell-sub" style="font-style: italic;">(Current Session)</span>
            </div>
          </article>
        </div>
      </section>
    </div>

    <!-- Confirm Dialogs -->
    <ConfirmDialog
      :visible="deleteDialog.visible"
      title="Delete Equipment"
      :message="`Are you sure you want to delete '${
        deleteDialog.item?.name || ''
      }'? This action cannot be undone.`"
      confirm-label="Delete"
      variant="danger"
      icon="delete"
      @confirm="executeDelete"
      @cancel="deleteDialog.visible = false"
    />

    <!-- Delete User Confirmation -->
    <ConfirmDialog
      :visible="userDeleteDialog.visible"
      title="Delete User Account"
      :message="`Are you sure you want to delete user '${
        userDeleteDialog.user?.username || ''
      }'? This will also remove all their active and past rentals. This action cannot be undone.`"
      confirm-label="Delete User"
      variant="danger"
      icon="delete"
      @confirm="executeDeleteUser"
      @cancel="userDeleteDialog.visible = false"
    />

    <!-- Reset DB Confirmation -->
    <ConfirmDialog
      :visible="resetDialog.visible"
      title="Reset System Database"
      :message="`WARNING: Are you sure you want to restore the database to its default factory seed state? This will completely clear all current rentals, custom devices, and non-default user accounts. This action is irreversible.`"
      confirm-label="Reset System"
      variant="danger"
      icon="warning"
      @confirm="executeReset"
      @cancel="resetDialog.visible = false"
    />

    <!-- Add User Modal Dialog -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div v-if="userModal.visible" class="dialog-overlay" @click.self="userModal.visible = false">
          <div class="dialog-card" role="dialog" aria-modal="true" style="max-width: 440px;">
            <h3 class="dialog-title" style="margin-bottom: 20px;">Create User Account</h3>
            <form @submit.prevent="executeCreateUser" style="display: flex; flex-direction: column; gap: 16px; text-align: left; width: 100%;">
              <label style="display: flex; flex-direction: column; gap: 6px; font-weight: 500;">
                <span>Username</span>
                <input v-model="userModal.username" type="text" required placeholder="e.g. jsmith" class="input-group" style="padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); width: 100%; font-size: 14px; background: var(--surface-card); color: var(--text-primary);" />
              </label>
              <label style="display: flex; flex-direction: column; gap: 6px; font-weight: 500;">
                <span>Password</span>
                <input v-model="userModal.password" type="password" required placeholder="••••••••" class="input-group" style="padding: 10px 14px; border-radius: 8px; border: 1px solid var(--border-color); width: 100%; font-size: 14px; background: var(--surface-card); color: var(--text-primary);" />
              </label>
              <label style="display: flex; align-items: center; gap: 10px; cursor: pointer; padding: 4px 0;">
                <input v-model="userModal.isAdmin" type="checkbox" style="width: 18px; height: 18px; cursor: pointer;" />
                <span style="font-weight: 500;">Administrator privileges</span>
              </label>
              <div class="dialog-actions" style="margin-top: 12px; display: flex; justify-content: flex-end; gap: 12px; width: 100%;">
                <button class="ghost-button" type="button" @click="userModal.visible = false" style="flex: 1;">Cancel</button>
                <button class="primary-button" type="submit" style="flex: 1;">Create User</button>
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
const query = ref("");
const statusFilter = ref("all");
const brandFilter = ref("all");
const sortBy = ref("name");

const activeTab = ref("equipment");
const userQuery = ref("");

const deleteDialog = reactive({
  visible: false,
  item: null,
});

const userModal = reactive({
  visible: false,
  username: "",
  password: "",
  isAdmin: false,
});

const userDeleteDialog = reactive({
  visible: false,
  user: null,
});

const resetDialog = reactive({
  visible: false,
});

const brands = computed(() =>
  [...new Set(hub.equipment.value.map((item) => item.brand))].sort()
);

const filteredEquipment = computed(() => {
  return hub.equipment.value
    .filter((item) => {
      const matchesSearch = [item.name, item.brand, item.serialNumber]
        .join(" ")
        .toLowerCase()
        .includes(query.value.toLowerCase());
      const matchesStatus =
        statusFilter.value === "all" || item.status === statusFilter.value;
      const matchesBrand =
        brandFilter.value === "all" || item.brand === brandFilter.value;
      return matchesSearch && matchesStatus && matchesBrand;
    })
    .sort((left, right) =>
      String(left[sortBy.value]).localeCompare(String(right[sortBy.value]))
    );
});

const filteredUsers = computed(() => {
  if (!hub.userDirectory.value) return [];
  return hub.userDirectory.value
    .filter((user) => {
      return user.username.toLowerCase().includes(userQuery.value.toLowerCase());
    })
    .sort((left, right) => left.username.localeCompare(right.username));
});

function statusClass(status) {
  if (status === "Available") return "status-available";
  if (status === "In use") return "status-in-use";
  if (status === "Repair") return "status-repair";
  return "";
}

function changeStatus(id, newStatus) {
  try {
    hub.saveEquipment(id, { status: newStatus });
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to update status."
    );
  }
}

function confirmDelete(item) {
  deleteDialog.item = item;
  deleteDialog.visible = true;
}

function executeDelete() {
  if (!deleteDialog.item) return;
  try {
    hub.deleteEquipmentItem(deleteDialog.item.id);
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to delete equipment."
    );
  }
  deleteDialog.visible = false;
  deleteDialog.item = null;
}

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
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "Failed to create user.");
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
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "Failed to delete user.");
  }
  userDeleteDialog.visible = false;
  userDeleteDialog.user = null;
}

function openResetConfirm() {
  resetDialog.visible = true;
}

async function executeReset() {
  try {
    await hub.resetDatabase();
    window.alert("Database has been successfully restored to factory seed state.");
  } catch (error) {
    window.alert(error instanceof Error ? error.message : "Failed to reset database.");
  }
  resetDialog.visible = false;
}
</script>

<style scoped>
.tabs-container {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  background: var(--surface-card);
  padding: 6px;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  width: max-content;
}

.tab-btn {
  padding: 8px 20px;
  font-size: 14px;
  font-weight: 600;
  border-radius: 8px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: var(--text-primary);
  background: var(--surface-hover);
}

.tab-btn.active {
  color: var(--surface-card);
  background: var(--text-primary);
}
</style>
