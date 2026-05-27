<template>
  <AppShell>
    <div class="admin-hero">
      <div>
        <p class="eyebrow">Operations Console</p>
        <h2>Hardware Management</h2>
        <p>Manage devices, user access, maintenance, and AI audits from one place.</p>
      </div>

      <div class="admin-hero-actions">
        <router-link class="primary-button" to="/admin/equipment/new">Add New Device</router-link>
        <router-link class="ghost-button" to="/audit">Run AI Audit</router-link>
      </div>
    </div>

    <section class="stats-row">
      <StatCard v-for="stat in dashboardStats" :key="stat.label" v-bind="stat" />
    </section>

    <section class="surface-card">
      <div class="table-shell desktop-only admin-table-shell">
        <div class="table-toolbar">
          <label class="input-group input-search compact">
            <span class="material-symbols-outlined">search</span>
            <input v-model="query" type="search" placeholder="Search hardware..." />
          </label>
          <button class="ghost-button" type="button" @click="hub.buildAuditReport()">Refresh Audit Snapshot</button>
        </div>

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
              <td><strong>{{ item.name }}</strong></td>
              <td>{{ item.brand }}</td>
              <td class="mono">{{ item.serialNumber }}</td>
              <td>{{ hub.formatDate(item.purchaseDate) }}</td>
              <td><StatusBadge :label="item.status" /></td>
              <td class="actions-cell align-right">
                <router-link class="icon-button" :to="`/admin/equipment/${item.id}`" title="Edit">
                  <span class="material-symbols-outlined">edit_square</span>
                </router-link>
                <button class="icon-button danger" type="button" title="Toggle Repair" @click="toggleRepair(item.id)">
                  <span class="material-symbols-outlined">build</span>
                </button>
                <button class="icon-button danger" type="button" title="Delete" @click="remove(item.id)">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card-list mobile-only">
        <article v-for="item in filteredEquipment" :key="item.id" class="device-card admin-card">
          <div>
            <p class="device-card-title">{{ item.name }}</p>
            <p class="device-card-meta">{{ item.brand }} · {{ item.serialNumber }}</p>
            <p class="device-card-meta">Added {{ hub.formatDate(item.purchaseDate) }}</p>
          </div>

          <StatusBadge :label="item.status" />

          <div class="card-actions">
            <router-link class="ghost-button small" :to="`/admin/equipment/${item.id}`">Edit</router-link>
            <button class="ghost-button small secondary" type="button" @click="toggleRepair(item.id)">Repair</button>
          </div>
        </article>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, ref } from 'vue';
import AppShell from '../components/AppShell.vue';
import StatCard from '../components/StatCard.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useHubState } from '../data/hubState';

const hub = useHubState();
const query = ref('');
const dashboardStats = computed(() => hub.dashboardStats.value);

const filteredEquipment = computed(() => {
  return hub.equipment.value.filter((item) => [item.name, item.brand, item.serialNumber].join(' ').toLowerCase().includes(query.value.toLowerCase()));
});

function toggleRepair(id) {
  try {
    hub.toggleRepairStatus(id);
  } catch (exception) {
    window.alert(exception instanceof Error ? exception.message : 'Unable to update repair status.');
  }
}

function remove(id) {
  if (!window.confirm('Delete this equipment item?')) {
    return;
  }

  try {
    hub.deleteEquipmentItem(id);
  } catch (exception) {
    window.alert(exception instanceof Error ? exception.message : 'Unable to delete equipment.');
  }
}
</script>
