<template>
  <AppShell>
    <div class="toolbar-grid single">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input v-model="query" type="search" placeholder="Search devices..." />
      </label>
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

const filteredRentals = computed(() => {
  return hub.openRentalsForCurrentUser.value
    .map((rental) => ({
      rental,
      item: hub.getEquipmentById(rental.equipmentId),
      id: rental.id,
    }))
    .filter(
      (entry) =>
        entry.item &&
        [entry.item.name, entry.item.brand, entry.item.serialNumber]
          .join(" ")
          .toLowerCase()
          .includes(query.value.toLowerCase())
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
