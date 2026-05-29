<template>
  <AppShell>
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
      <button class="primary-button small" type="button" @click="openAddDevice">
        <span class="material-symbols-outlined">add</span>
        Add Device
      </button>
    </div>

    <section class="surface-card">
      <div class="table-shell desktop-only">
        <table class="compact-table">
          <thead>
            <tr>
              <th class="sortable-th" @click="toggleSort('name')">
                Device <span class="sort-arrow">{{ sortArrow("name") }}</span>
              </th>
              <th class="sortable-th" @click="toggleSort('serialNumber')">
                Serial
                <span class="sort-arrow">{{ sortArrow("serialNumber") }}</span>
              </th>
              <th class="sortable-th" @click="toggleSort('purchaseDate')">
                Purchased
                <span class="sort-arrow">{{ sortArrow("purchaseDate") }}</span>
              </th>
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
                {{
                  item.purchaseDate ? hub.formatDate(item.purchaseDate) : "—"
                }}
              </td>
              <td>
                <StatusBadge :label="item.status" />
              </td>
              <td class="actions-cell align-right">
                <button
                  class="icon-button"
                  type="button"
                  title="Edit"
                  @click="openEditDevice(item)"
                >
                  <span class="material-symbols-outlined">edit</span>
                </button>
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
            <p class="device-card-meta" v-if="item.purchaseDate">
              {{ hub.formatDate(item.purchaseDate) }}
            </p>
          </div>
          <StatusBadge :label="item.status" />
          <div class="card-actions">
            <button
              class="ghost-button small"
              type="button"
              @click="openEditDevice(item)"
            >
              Edit
            </button>
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
      :message="`Delete '${deleteDialog.item?.name || ''}'? This cannot be undone.`"
      confirm-label="Delete"
      variant="danger"
      icon="delete"
      @confirm="executeDelete"
      @cancel="deleteDialog.visible = false"
    />

    <!-- Add/Edit Device Modal -->
    <Teleport to="body">
      <Transition name="dialog-fade">
        <div
          v-if="deviceModal.visible"
          class="dialog-overlay"
          @click.self="deviceModal.visible = false"
        >
          <div
            class="dialog-card dialog-form-card"
            role="dialog"
            aria-modal="true"
          >
            <h3 class="dialog-title">
              {{ deviceModal.isNew ? "Add Device" : "Edit Device" }}
            </h3>
            <form class="edit-form" @submit.prevent="saveDevice">
              <label>
                <span>Device Name</span>
                <input v-model="deviceModal.form.name" type="text" required />
              </label>
              <label>
                <span>Brand</span>
                <input v-model="deviceModal.form.brand" type="text" required />
              </label>
              <label>
                <span>Serial Number</span>
                <input
                  v-model="deviceModal.form.serialNumber"
                  type="text"
                  required
                />
              </label>
              <label>
                <span>Purchase Date</span>
                <input
                  v-model="deviceModal.form.purchaseDate"
                  type="date"
                  required
                />
              </label>
              <label>
                <span>Status</span>
                <select v-model="deviceModal.form.status">
                  <option value="Available">Available</option>
                  <option value="In use">In Use</option>
                  <option value="Repair">Repair</option>
                </select>
              </label>
              <div class="dialog-actions">
                <button
                  class="ghost-button"
                  type="button"
                  @click="deviceModal.visible = false"
                >
                  Cancel
                </button>
                <button class="primary-button" type="submit">
                  {{ deviceModal.isNew ? "Create" : "Save" }}
                </button>
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
import StatusBadge from "../components/StatusBadge.vue";
import ConfirmDialog from "../components/ConfirmDialog.vue";
import { useHubState } from "../data/hubState";

const hub = useHubState();
const query = ref("");
const statusFilter = ref("all");
const brandFilter = ref("all");
const sortKey = ref("name");
const sortAsc = ref(true);

const deleteDialog = reactive({ visible: false, item: null });
const deviceModal = reactive({
  visible: false,
  isNew: true,
  editId: null,
  form: {
    name: "",
    brand: "",
    serialNumber: "",
    purchaseDate: "",
    status: "Available",
  },
});

const brands = computed(() =>
  [...new Set(hub.equipment.value.map((i) => i.brand))].sort(),
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
    .sort((a, b) => {
      const av = String(a[sortKey.value] || "");
      const bv = String(b[sortKey.value] || "");
      const cmp = av.localeCompare(bv);
      return sortAsc.value ? cmp : -cmp;
    });
});

function toggleSort(key) {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value;
  } else {
    sortKey.value = key;
    sortAsc.value = true;
  }
}

function sortArrow(key) {
  if (sortKey.value !== key) return "↕";
  return sortAsc.value ? "↑" : "↓";
}

function openAddDevice() {
  deviceModal.isNew = true;
  deviceModal.editId = null;
  deviceModal.form = {
    name: "",
    brand: "",
    serialNumber: "",
    purchaseDate: new Date().toISOString().slice(0, 10),
    status: "Available",
  };
  deviceModal.visible = true;
}

function openEditDevice(item) {
  deviceModal.isNew = false;
  deviceModal.editId = item.id;
  deviceModal.form = {
    name: item.name,
    brand: item.brand,
    serialNumber: item.serialNumber,
    purchaseDate: item.purchaseDate || "",
    status: item.status,
  };
  deviceModal.visible = true;
}

async function saveDevice() {
  try {
    if (deviceModal.isNew) {
      await hub.createEquipmentItem(deviceModal.form);
    } else {
      await hub.saveEquipment(deviceModal.editId, deviceModal.form);
    }
    deviceModal.visible = false;
  } catch (e) {
    window.alert(e instanceof Error ? e.message : "Failed to save device.");
  }
}

function confirmDelete(item) {
  deleteDialog.item = item;
  deleteDialog.visible = true;
}

async function executeDelete() {
  if (!deleteDialog.item) return;
  try {
    await hub.deleteEquipmentItem(deleteDialog.item.id);
  } catch (e) {
    window.alert(e instanceof Error ? e.message : "Failed to delete.");
  }
  deleteDialog.visible = false;
  deleteDialog.item = null;
}
</script>
