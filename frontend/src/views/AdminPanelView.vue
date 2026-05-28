<template>
  <AppShell>
    <div class="toolbar-grid wide">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input v-model="query" type="search" placeholder="Search devices..." />
      </label>
      <select v-model="statusFilter" class="input-group input-select">
        <option value="all">All statuses</option>
        <option value="Available">Available</option>
        <option value="InUse">In use</option>
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

      <button
        class="primary-button"
        type="button"
        @click="$router.push('/admin/equipment/new')"
      >
        <span class="material-symbols-outlined">add</span>
        Add Device
      </button>
    </div>

    <section class="surface-card">
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
                  <option value="InUse">In Use</option>
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
            <option value="InUse">In Use</option>
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

const deleteDialog = reactive({
  visible: false,
  item: null,
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

function statusClass(status) {
  if (status === "Available") return "status-available";
  if (status === "InUse") return "status-in-use";
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
</script>
