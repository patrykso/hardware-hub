<template>
  <AppShell>
    <div class="toolbar-grid">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input
          v-model="searchText"
          type="search"
          placeholder="Search devices..."
        />
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
        <option value="purchaseDate">Sort by date</option>
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
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredEquipment" :key="item.id">
              <td>
                <strong>{{ item.name }}</strong>
                <span class="cell-sub">{{ item.brand }}</span>
              </td>
              <td class="mono">{{ item.serialNumber }}</td>
              <td><StatusBadge :label="item.status" /></td>
              <td class="actions-cell">
                <button
                  v-if="item.status === 'Available'"
                  class="ghost-button small"
                  type="button"
                  @click="rent(item.id)"
                >
                  Rent
                </button>
                <button
                  v-else
                  class="ghost-button secondary small"
                  type="button"
                  disabled
                >
                  Unavailable
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

          <StatusBadge :label="item.status" />

          <button
            v-if="item.status === 'Available'"
            class="primary-button small"
            type="button"
            @click="rent(item.id)"
          >
            Rent
          </button>
          <button
            v-else
            class="ghost-button secondary small"
            type="button"
            disabled
          >
            Unavailable
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
const searchText = ref("");
const statusFilter = ref("all");
const brandFilter = ref("all");
const sortBy = ref("name");

const brands = computed(() =>
  [...new Set(hub.equipment.value.map((item) => item.brand))].sort()
);

const filteredEquipment = computed(() => {
  return hub.equipment.value
    .filter((item) => {
      const matchesSearch = [item.name, item.brand, item.serialNumber]
        .join(" ")
        .toLowerCase()
        .includes(searchText.value.toLowerCase());
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

function rent(id) {
  try {
    hub.rentEquipment(id);
  } catch (exception) {
    window.alert(
      exception instanceof Error
        ? exception.message
        : "Unable to rent equipment."
    );
  }
}
</script>
