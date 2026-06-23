<template>
  <AppShell>
    <div class="toolbar-grid">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input v-model="query" type="search" placeholder="Search devices or users..." />
      </label>
      <select v-model="brandFilter" class="input-group input-select">
        <option value="all">All brands</option>
        <option v-for="brand in brands" :key="brand" :value="brand">
          {{ brand }}
        </option>
      </select>
      <select v-model="statusFilter" class="input-group input-select">
        <option value="all">All status</option>
        <option value="active">Active (In Use)</option>
        <option value="returned">Returned</option>
      </select>
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
              <th class="sortable-th" @click="toggleSort('username')">
                Rented By
                <span class="sort-arrow">{{ sortArrow("username") }}</span>
              </th>
              <th class="sortable-th" @click="toggleSort('rentedAt')">
                Rented At
                <span class="sort-arrow">{{ sortArrow("rentedAt") }}</span>
              </th>
              <th class="sortable-th" @click="toggleSort('returnedAt')">
                Returned At
                <span class="sort-arrow">{{ sortArrow("returnedAt") }}</span>
              </th>
              <th class="align-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredRentals.length === 0">
              <td colspan="6">
                <div class="empty-state">
                  <span class="material-symbols-outlined">history_edu</span>
                  <p>No rentals found matching the criteria.</p>
                </div>
              </td>
            </tr>
            <tr v-for="entry in filteredRentals" :key="entry.id">
              <td>
                <strong>{{ entry.item.name }}</strong>
                <span class="cell-sub">{{ entry.item.brand }}</span>
              </td>
              <td class="mono">{{ entry.item.serialNumber }}</td>
              <td>
                <span class="badge user-badge">{{ entry.username }}</span>
              </td>
              <td>{{ hub.formatDateTime(entry.rental.rentedAt) }}</td>
              <td>
                <span v-if="entry.rental.returnedAt">
                  {{ hub.formatDateTime(entry.rental.returnedAt) }}
                </span>
                <StatusBadge v-else label="In Use" />
              </td>
              <td class="actions-cell align-right">
                <button
                  v-if="!entry.rental.returnedAt"
                  class="primary-button small"
                  type="button"
                  @click="returnRental(entry.id)"
                >
                  Return
                </button>
                <span v-else class="text-muted small">Returned</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card-list mobile-only">
        <article
          v-for="entry in filteredRentals"
          :key="entry.id"
          class="device-card"
        >
          <div style="flex-grow: 1;">
            <p class="device-card-title">{{ entry.item.name }}</p>
            <p class="device-card-meta">
              {{ entry.item.brand }} · {{ entry.item.serialNumber }}
            </p>
            <div style="margin-top: 8px; display: flex; gap: 8px; align-items: center; flex-wrap: wrap;">
              <span class="badge user-badge" style="font-size: 0.75rem;">By: {{ entry.username }}</span>
              <span class="text-muted" style="font-size: 0.75rem;">Rented: {{ hub.formatDate(entry.rental.rentedAt) }}</span>
            </div>
          </div>
          <div style="text-align: right; display: flex; flex-direction: column; gap: 8px; align-items: flex-end;">
            <StatusBadge v-if="!entry.rental.returnedAt" label="In Use" />
            <span v-else class="text-muted small">Returned {{ hub.formatDate(entry.rental.returnedAt) }}</span>
            <button
              v-if="!entry.rental.returnedAt"
              class="primary-button small"
              type="button"
              @click="returnRental(entry.id)"
            >
              Return
            </button>
          </div>
        </article>
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
const brandFilter = ref("all");
const statusFilter = ref("all");
const sortKey = ref("rentedAt");
const sortAsc = ref(false);

const userMap = computed(() => {
  const map = {};
  if (hub.userDirectory.value) {
    hub.userDirectory.value.forEach((u) => {
      map[u.id] = u.username;
    });
  }
  return map;
});

const brands = computed(() => {
  const items = hub.rentals.value
    .map((r) => hub.getEquipmentById(r.equipmentId))
    .filter(Boolean);
  return [...new Set(items.map((i) => i.brand))].sort();
});

const filteredRentals = computed(() => {
  return hub.rentals.value
    .map((rental) => {
      const item = hub.getEquipmentById(rental.equipmentId);
      const username = userMap.value[rental.userId] || `User #${rental.userId}`;
      return {
        rental,
        item,
        username,
        id: rental.id,
      };
    })
    .filter((entry) => {
      if (!entry.item) return false;

      // Status filter
      if (statusFilter.value === "active" && entry.rental.returnedAt) return false;
      if (statusFilter.value === "returned" && !entry.rental.returnedAt) return false;

      // Brand filter
      if (brandFilter.value !== "all" && entry.item.brand !== brandFilter.value) return false;

      // Text search
      const searchStr = [
        entry.item.name,
        entry.item.brand,
        entry.item.serialNumber,
        entry.username,
      ]
        .join(" ")
        .toLowerCase();
      
      return searchStr.includes(query.value.toLowerCase());
    })
    .sort((a, b) => {
      let av, bv;
      if (sortKey.value === "name") {
        av = a.item.name;
        bv = b.item.name;
      } else if (sortKey.value === "serialNumber") {
        av = a.item.serialNumber;
        bv = b.item.serialNumber;
      } else if (sortKey.value === "username") {
        av = a.username;
        bv = b.username;
      } else if (sortKey.value === "rentedAt") {
        av = a.rental.rentedAt;
        bv = b.rental.rentedAt;
      } else if (sortKey.value === "returnedAt") {
        av = a.rental.returnedAt || "9999-12-31";
        bv = b.rental.returnedAt || "9999-12-31";
      }

      const cmp = String(av || "").localeCompare(String(bv || ""));
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

function returnRental(id) {
  hub
    .returnRental(id)
    .catch((e) =>
      window.alert(
        e instanceof Error ? e.message : "Unable to return equipment.",
      ),
    );
}
</script>

<style scoped>
.user-badge {
  background-color: var(--color-background-soft);
  color: var(--color-text-normal);
  border: 1px solid var(--color-border);
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 500;
}
.toolbar-grid {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  margin-bottom: 20px;
}
@media (max-width: 768px) {
  .toolbar-grid {
    grid-template-columns: 1fr;
  }
}
</style>
