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

      <select v-model="sortBy" class="input-group input-select">
        <option value="name">Sort by name</option>
        <option value="brand">Sort by brand</option>
      </select>
    </div>

    <section class="surface-card">
      <div class="table-shell desktop-only">
        <table class="compact-table">
          <thead>
            <tr>
              <th>Device</th>
              <th>Serial</th>
              <th>Status</th>
              <th class="align-right">Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="filteredRentals.length === 0">
              <td colspan="4">
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
              <td><StatusBadge label="Active" /></td>
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
          </div>

          <StatusBadge label="Active" />
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
const sortBy = ref("name");

const brands = computed(() => {
  const rentalItems = hub.openRentalsForCurrentUser.value
    .map((r) => hub.getEquipmentById(r.equipmentId))
    .filter(Boolean);
  return [...new Set(rentalItems.map((item) => item.brand))].sort();
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
    .sort((a, b) =>
      String(a.item[sortBy.value]).localeCompare(String(b.item[sortBy.value]))
    );
});

function returnRental(id) {
  try {
    hub.returnRental(id);
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to return equipment."
    );
  }
}
</script>
