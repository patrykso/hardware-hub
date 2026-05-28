<template>
  <AppShell>
    <section class="surface-card form-layout">
      <div class="form-header">
        <div>
          <p class="eyebrow">Admin Panel</p>
          <h2>Edit Equipment</h2>
          <p>Update core inventory details or move an item into Repair when it is safe to do so.</p>
        </div>
        <StatusBadge :label="form.status" />
      </div>

      <form class="edit-form" @submit.prevent="save">
        <label>
          <span>Device Name</span>
          <input v-model="form.name" type="text" required />
        </label>

        <label>
          <span>Brand</span>
          <input v-model="form.brand" type="text" required />
        </label>

        <label>
          <span>Serial Number</span>
          <input v-model="form.serialNumber" type="text" required />
        </label>

        <label>
          <span>Purchase Date</span>
          <input v-model="form.purchaseDate" type="date" required />
        </label>

        <label>
          <span>Status</span>
          <select v-model="form.status">
            <option value="Available">Available</option>
            <option value="In use">In use</option>
            <option value="Repair">Repair</option>
          </select>
        </label>

        <div class="form-actions">
          <button class="ghost-button" type="button" @click="toggleRepair">Toggle Repair</button>
          <button class="primary-button" type="submit">Save Changes</button>
        </div>
      </form>
    </section>
  </AppShell>
</template>

<script setup>
import { computed, reactive } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import AppShell from '../components/AppShell.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useHubState } from '../data/hubState';

const hub = useHubState();
const route = useRoute();
const router = useRouter();

const currentItem = computed(() => {
  if (route.params.id === 'new') {
    return {
      id: null,
      name: '',
      brand: '',
      serialNumber: '',
      purchaseDate: new Date().toISOString().slice(0, 10),
      status: 'Available',
    };
  }

  return hub.cloneEquipmentItem(hub.getEquipmentById(route.params.id) || {});
});

const form = reactive({
  name: currentItem.value.name,
  brand: currentItem.value.brand,
  serialNumber: currentItem.value.serialNumber,
  purchaseDate: currentItem.value.purchaseDate,
  status: currentItem.value.status,
});

function save() {
  try {
    if (route.params.id === 'new') {
      hub.createEquipmentItem(form);
    } else {
      hub.saveEquipment(route.params.id, form);
    }

    router.push('/admin');
  } catch (exception) {
    window.alert(exception instanceof Error ? exception.message : 'Unable to save equipment.');
  }
}

function toggleRepair() {
  try {
    if (route.params.id === 'new') {
      form.status = form.status === 'Repair' ? 'Available' : 'Repair';
      return;
    }

    hub.toggleRepairStatus(route.params.id);
    const refreshed = hub.getEquipmentById(route.params.id);
    if (refreshed) {
      form.status = refreshed.status;
    }
  } catch (exception) {
    window.alert(exception instanceof Error ? exception.message : 'Unable to toggle repair status.');
  }
}
</script>
