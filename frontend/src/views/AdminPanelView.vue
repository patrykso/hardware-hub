<template>
  <AppShell>
    <section class="admin-page">
      <header class="admin-topbar surface-card admin-topbar-surface">
        <div class="admin-topbar-title">Admin Panel</div>

        <label class="input-group admin-search">
          <span class="material-symbols-outlined">search</span>
          <input
            v-model="query"
            type="search"
            placeholder="Search for device, brand, or serial number..."
          />
        </label>

        <div class="admin-topbar-avatar" :title="currentUserName">
          {{ currentUserInitials }}
        </div>
      </header>

      <div class="admin-content">
        <div class="admin-heading-row">
          <h2>Hardware Management</h2>
          <button
            class="primary-button admin-add-button"
            type="button"
            @click="$router.push('/admin/equipment/new')"
          >
            <span class="material-symbols-outlined">add</span>
            Add New Device
          </button>
        </div>

        <section class="surface-card admin-table-card">
          <div class="table-shell desktop-only admin-table-shell">
            <table>
              <thead>
                <tr>
                  <th>Device Name</th>
                  <th>Brand</th>
                  <th>Serial Number</th>
                  <th>Date Added</th>
                  <th>Status</th>
                  <th class="align-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in filteredEquipment" :key="item.id">
                  <td>
                    <strong>{{ item.name }}</strong>
                  </td>
                  <td>{{ item.brand }}</td>
                  <td class="mono">{{ item.serialNumber }}</td>
                  <td>{{ hub.formatDate(item.purchaseDate) }}</td>
                  <td><StatusBadge :label="item.status" /></td>
                  <td class="actions-cell align-right">
                    <router-link
                      class="icon-button"
                      :to="`/admin/equipment/${item.id}`"
                      title="Edit"
                    >
                      <span class="material-symbols-outlined">edit_square</span>
                    </router-link>
                    <button
                      class="icon-button danger"
                      type="button"
                      title="Delete"
                      @click="remove(item.id)"
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
              class="device-card admin-card"
            >
              <div>
                <p class="device-card-title">{{ item.name }}</p>
                <p class="device-card-meta">
                  {{ item.brand }} · {{ item.serialNumber }}
                </p>
                <p class="device-card-meta">
                  Added {{ hub.formatDate(item.purchaseDate) }}
                </p>
              </div>

              <StatusBadge :label="item.status" />

              <div class="card-actions">
                <router-link
                  class="ghost-button small"
                  :to="`/admin/equipment/${item.id}`"
                  >Edit</router-link
                >
              </div>
            </article>
          </div>
        </section>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, ref } from "vue";
import AppShell from "../components/AppShell.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { useHubState } from "../data/hubState";

const hub = useHubState();
const query = ref("");

const currentUserName = computed(
  () => hub.currentUser.value?.displayName || "User"
);
const currentUserInitials = computed(() => {
  return currentUserName.value
    .split(" ")
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
});

const filteredEquipment = computed(() => {
  return hub.equipment.value.filter((item) =>
    [item.name, item.brand, item.serialNumber]
      .join(" ")
      .toLowerCase()
      .includes(query.value.toLowerCase())
  );
});

function toggleRepair(id) {
  try {
    hub.toggleRepairStatus(id);
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to update repair status."
    );
  }
}

function remove(id) {
  if (!window.confirm("Delete this equipment item?")) {
    return;
  }

  try {
    hub.deleteEquipmentItem(id);
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to delete equipment."
    );
  }
}
</script>
