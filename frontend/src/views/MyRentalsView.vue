<template>
  <AppShell>
    <div class="toolbar-grid narrow">
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
              <th class="align-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredRentals.length === 0">
              <td colspan="5">
                <div class="empty-state">
                  <span class="material-symbols-outlined">assignment</span>
                  <p>You don't have any active rentals.</p>
                </div>
              </td>
            </tr>
            <tr v-for="rental in filteredRentals" :key="rental.id">
              <td>
                <strong>{{ rental.item.name }}</strong>
                <span class="cell-sub">{{ rental.item.brand }}</span>
              </td>
              <td class="mono">{{ rental.item.serialNumber }}</td>
              <td class="cell-sub">
                {{
                  rental.item.purchaseDate
                    ? hub.formatDate(rental.item.purchaseDate)
                    : "—"
                }}
              </td>
              <td><StatusBadge label="InUse" /></td>
              <td class="actions-cell align-right">
                <button
                  class="primary-button small"
                  type="button"
                  @click="returnRental(rental.id)"
                >
                  Return
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card-list mobile-only">
        <article
          v-for="rental in filteredRentals"
          :key="rental.id"
          class="device-card"
        >
          <div>
            <p class="device-card-title">{{ rental.item.name }}</p>
            <p class="device-card-meta">
              {{ rental.item.brand }} · {{ rental.item.serialNumber }}
            </p>
            <p class="device-card-meta" v-if="rental.item.purchaseDate">
              {{ hub.formatDate(rental.item.purchaseDate) }}
            </p>
          </div>
          <StatusBadge label="InUse" />
          <button
            class="primary-button small"
            type="button"
            @click="returnRental(rental.id)"
          >
            Return
          </button>
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
const statusFilter = ref("all");
const brandFilter = ref("all");
const sortKey = ref("name");
const sortAsc = ref(true);

const brands = computed(() => {
  const items = hub.openRentalsForCurrentUser.value
    .map((r) => hub.getEquipmentById(r.equipmentId))
    .filter(Boolean);
  return [...new Set(items.map((i) => i.brand))].sort();
});

const filteredRentals = computed(() => {
  return hub.openRentalsForCurrentUser.value
    .map((rental) => ({
      rental,
      item: hub.getEquipmentById(rental.equipmentId),
      id: rental.id,
    }))
    .filter((entry) => {
      if (!entry.item) return false;
      const matchesSearch = [
        entry.item.name,
        entry.item.brand,
        entry.item.serialNumber,
      ]
        .join(" ")
        .toLowerCase()
        .includes(query.value.toLowerCase());
      const matchesStatus =
        statusFilter.value === "all" ||
        entry.item.status === statusFilter.value;
      const matchesBrand =
        brandFilter.value === "all" || entry.item.brand === brandFilter.value;
      return matchesSearch && matchesStatus && matchesBrand;
    })
    .sort((a, b) => {
      const av = String(a.item[sortKey.value] || "");
      const bv = String(b.item[sortKey.value] || "");
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
