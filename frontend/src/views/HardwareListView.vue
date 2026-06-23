<template>
  <AppShell>
    <div class="toolbar-grid narrow">
      <label class="input-group input-search">
        <span class="material-symbols-outlined">search</span>
        <input
          v-model="searchText"
          type="search"
          placeholder="Search devices..."
        />
      </label>

      <!-- Brand Multichoice Dropdown -->
      <div id="brand-dropdown-container" class="custom-dropdown">
        <div
          class="dropdown-trigger"
          :class="{ open: brandDropdownOpen }"
          @click="toggleBrandDropdown"
        >
          <span class="dropdown-trigger-text">{{ selectedBrandsLabel }}</span>
          <span class="material-symbols-outlined">expand_more</span>
        </div>
        <div v-if="brandDropdownOpen" class="dropdown-menu">
          <label v-for="brand in brands" :key="brand" class="dropdown-item">
            <input
              type="checkbox"
              :value="brand"
              v-model="selectedBrands"
              class="checkbox-input"
            />
            <span class="checkbox-text-label">{{ brand }}</span>
          </label>
        </div>
      </div>

      <!-- Status Multichoice Dropdown -->
      <div id="status-dropdown-container" class="custom-dropdown">
        <div
          class="dropdown-trigger"
          :class="{ open: statusDropdownOpen }"
          @click="toggleStatusDropdown"
        >
          <span class="dropdown-trigger-text">{{ selectedStatusesLabel }}</span>
          <span class="material-symbols-outlined">expand_more</span>
        </div>
        <div v-if="statusDropdownOpen" class="dropdown-menu">
          <label v-for="statusItem in availableStatuses" :key="statusItem" class="dropdown-item">
            <input
              type="checkbox"
              :value="statusItem"
              v-model="selectedStatuses"
              class="checkbox-input"
            />
            <span class="checkbox-text-label">{{ statusItem }}</span>
          </label>
        </div>
      </div>
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
              <td>
                {{
                  item.purchaseDate ? hub.formatDate(item.purchaseDate) : "—"
                }}
              </td>
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
            <tr v-if="filteredEquipment.length === 0">
              <td colspan="5">
                <div class="empty-state">
                  <span class="material-symbols-outlined">devices_off</span>
                  <p>No hardware matching your filters was found.</p>
                </div>
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
        <div v-if="filteredEquipment.length === 0" class="empty-state">
          <span class="material-symbols-outlined">devices_off</span>
          <p>No hardware matching your filters was found.</p>
        </div>
      </div>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, ref, onMounted, onUnmounted } from "vue";
import AppShell from "../components/AppShell.vue";
import StatusBadge from "../components/StatusBadge.vue";
import { useHubState } from "../data/hubState";

const hub = useHubState();
const searchText = ref("");

// Multichoice filter states
const selectedStatuses = ref([]);
const selectedBrands = ref([]);

// Dropdown UI states
const brandDropdownOpen = ref(false);
const statusDropdownOpen = ref(false);

const sortKey = ref("name");
const sortAsc = ref(true);

function toggleBrandDropdown() {
  brandDropdownOpen.value = !brandDropdownOpen.value;
  statusDropdownOpen.value = false;
}

function toggleStatusDropdown() {
  statusDropdownOpen.value = !statusDropdownOpen.value;
  brandDropdownOpen.value = false;
}

// Click outside handler to close dropdowns
function handleClickOutside(event) {
  const brandEl = document.getElementById("brand-dropdown-container");
  const statusEl = document.getElementById("status-dropdown-container");
  if (brandEl && !brandEl.contains(event.target)) {
    brandDropdownOpen.value = false;
  }
  if (statusEl && !statusEl.contains(event.target)) {
    statusDropdownOpen.value = false;
  }
}

onMounted(() => {
  window.addEventListener("click", handleClickOutside);
});

onUnmounted(() => {
  window.removeEventListener("click", handleClickOutside);
});

// Brands available based on visible equipment
const brands = computed(() => {
  const items = hub.equipmentForCurrentUser.value || [];
  return [...new Set(items.map((i) => i.brand).filter(Boolean))].sort();
});

// Statuses visible to the user (non-admin can see all except Error)
const availableStatuses = computed(() => {
  if (hub.currentUser.value?.isAdmin) {
    return ["Available", "In use", "Repair", "Error"];
  }
  return ["Available", "In use", "Repair"];
});

// Computed labels for triggers
const selectedBrandsLabel = computed(() => {
  if (selectedBrands.value.length === 0) return "All brands";
  if (selectedBrands.value.length === brands.value.length) return "All brands";
  return selectedBrands.value.join(", ");
});

const selectedStatusesLabel = computed(() => {
  if (selectedStatuses.value.length === 0) return "All statuses";
  if (selectedStatuses.value.length === availableStatuses.value.length) return "All statuses";
  return selectedStatuses.value.join(", ");
});

const filteredEquipment = computed(() => {
  const source = hub.equipmentForCurrentUser.value || [];
  return source
    .filter((item) => {
      const matchesSearch = [item.name, item.brand, item.serialNumber]
        .join(" ")
        .toLowerCase()
        .includes(searchText.value.toLowerCase());

      // Status filtering
      let matchesStatus = true;
      if (selectedStatuses.value.length > 0) {
        matchesStatus = selectedStatuses.value.includes(item.status);
      }

      // Brand filtering
      let matchesBrand = true;
      if (selectedBrands.value.length > 0) {
        matchesBrand = selectedBrands.value.includes(item.brand);
      }

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

function rent(id) {
  hub
    .rentEquipment(id)
    .catch((e) =>
      window.alert(
        e instanceof Error ? e.message : "Unable to rent equipment.",
      ),
    );
}
</script>

<style scoped>
.custom-dropdown {
  position: relative;
  width: 100%;
}

.dropdown-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  padding: 0 14px;
  min-height: 48px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--panel-muted);
  cursor: pointer;
  user-select: none;
  transition: border-color 180ms, box-shadow 180ms;
}

.dropdown-trigger:hover {
  border-color: var(--line-strong);
}

.dropdown-trigger.open {
  border-color: rgba(37, 99, 235, 0.4);
  box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.08);
}

.dropdown-trigger-text {
  flex: 1;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  font-size: 0.95rem;
}

.dropdown-menu {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 6px;
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 14px;
  box-shadow: var(--shadow);
  z-index: 100;
  max-height: 240px;
  overflow-y: auto;
  padding: 8px 0;
  backdrop-filter: blur(8px);
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  cursor: pointer;
  user-select: none;
  transition: background 150ms ease;
  font-size: 0.95rem;
}

.dropdown-item:hover {
  background: var(--panel-muted);
}

.dropdown-item input[type="checkbox"] {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1px solid var(--line);
  cursor: pointer;
  accent-color: var(--blue);
}

.checkbox-text-label {
  flex: 1;
}

.checkbox-input {
  width: 18px;
  height: 18px;
  border-radius: 6px;
  border: 1px solid var(--line);
  cursor: pointer;
  accent-color: var(--blue);
}
</style>
