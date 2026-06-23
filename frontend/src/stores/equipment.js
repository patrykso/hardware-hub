import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';
import axios from '../api/axios';

// Helpers to map camelCase <-> snake_case
function mapEquipmentFromBackend(item) {
  return {
    id: item.id,
    name: item.name || '',
    brand: item.brand || '',
    serialNumber: item.serial_number || '',
    purchaseDate: item.purchase_date ? item.purchase_date.slice(0, 10) : '',
    status: item.status || '',
    notes: item.notes || '',
    history: item.history || '',
    assignedTo: item.assigned_to || '',
  };
}

function mapEquipmentToBackend(payload) {
  return {
    name: payload.name ? payload.name.trim() : '',
    brand: payload.brand ? payload.brand.trim() : '',
    serial_number: payload.serialNumber ? payload.serialNumber.trim() : '',
    purchase_date: payload.purchaseDate ? payload.purchaseDate.slice(0, 10) : null,
    status: payload.status,
    notes: payload.notes || null,
    history: payload.history || null,
    assigned_to: payload.assignedTo || null,
  };
}

function mapRentalFromBackend(rental) {
  return {
    id: rental.id,
    equipmentId: rental.equipment_id,
    userId: rental.user_id,
    rentedAt: rental.rented_at,
    returnedAt: rental.returned_at,
  };
}

export const useEquipmentStore = defineStore('equipment', () => {
  const authStore = useAuthStore();

  const equipment = ref([]);
  const rentals = ref([]);
  const auditReport = ref(null);

  function getEquipmentById(id) {
    return equipment.value.find((item) => item.id === Number(id));
  }

  function getOpenRentalForEquipment(equipmentId) {
    return rentals.value.find((rental) => rental.equipmentId === Number(equipmentId) && !rental.returnedAt);
  }

  async function fetchEquipment() {
    try {
      const response = await axios.get('/api/v1/equipment');
      equipment.value = response.data.map(mapEquipmentFromBackend);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to fetch equipment.';
      throw new Error(detail);
    }
  }

  async function fetchRentals() {
    try {
      const response = await axios.get('/api/v1/rentals');
      rentals.value = response.data.map(mapRentalFromBackend);
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to fetch rentals.';
      throw new Error(detail);
    }
  }

  async function fetchData() {
    if (!authStore.isAuthenticated) return;
    try {
      await Promise.all([fetchEquipment(), fetchRentals()]);
    } catch (err) {
      console.error('Failed to pre-fetch equipment or rentals:', err);
    }
  }

  async function rentEquipment(equipmentId) {
    if (!authStore.currentUser) {
      throw new Error('You must be logged in to rent equipment.');
    }

    try {
      await axios.post('/api/v1/rentals', {
        equipment_id: Number(equipmentId),
      });
      await fetchData();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to rent equipment.';
      throw new Error(detail);
    }
  }

  async function returnRental(rentalId) {
    if (!authStore.currentUser) {
      throw new Error('You must be logged in to return equipment.');
    }

    try {
      await axios.post(`/api/v1/rentals/${rentalId}/return`);
      await fetchData();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to return equipment.';
      throw new Error(detail);
    }
  }

  async function toggleRepairStatus(equipmentId) {
    const item = getEquipmentById(equipmentId);
    if (!item) {
      throw new Error('Equipment not found.');
    }

    if (item.status === 'In use') {
      throw new Error('Equipment in use must be returned before it can be moved to Repair.');
    }

    const newStatus = item.status === 'Repair' ? 'Available' : 'Repair';
    try {
      await axios.patch(`/api/v1/equipment/${equipmentId}`, {
        status: newStatus,
      });
      await fetchEquipment();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to toggle repair status.';
      throw new Error(detail);
    }
  }

  async function saveEquipment(equipmentId, patch) {
    const item = getEquipmentById(equipmentId);
    if (!item) {
      throw new Error('Equipment not found.');
    }

    const openRental = getOpenRentalForEquipment(equipmentId);
    if (openRental && patch.status && patch.status !== 'In use') {
      throw new Error('Equipment currently in use cannot be moved away from In use status without returning it first.');
    }

    if (patch.status === 'Repair' && item.status === 'In use') {
      throw new Error('Cannot set an item to Repair while it is In use.');
    }

    const payload = {};
    if (patch.name !== undefined) payload.name = patch.name ? patch.name.trim() : '';
    if (patch.brand !== undefined) payload.brand = patch.brand ? patch.brand.trim() : '';
    if (patch.serialNumber !== undefined) payload.serial_number = patch.serialNumber ? patch.serialNumber.trim() : '';
    if (patch.purchaseDate !== undefined) payload.purchase_date = patch.purchaseDate ? patch.purchaseDate.slice(0, 10) : null;
    if (patch.status !== undefined) payload.status = patch.status;
    if (patch.notes !== undefined) payload.notes = patch.notes;
    if (patch.history !== undefined) payload.history = patch.history;
    if (patch.assignedTo !== undefined) payload.assigned_to = patch.assignedTo;

    try {
      await axios.patch(`/api/v1/equipment/${equipmentId}`, payload);
      await fetchEquipment();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to save equipment.';
      throw new Error(detail);
    }
  }

  async function createEquipmentItem(payload) {
    const data = mapEquipmentToBackend(payload);
    try {
      await axios.post('/api/v1/equipment', data);
      await fetchEquipment();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to create equipment.';
      throw new Error(detail);
    }
  }

  async function deleteEquipmentItem(equipmentId) {
    const item = getEquipmentById(equipmentId);
    if (!item) {
      throw new Error('Equipment not found.');
    }

    if (item.status === 'In use') {
      throw new Error('Cannot delete equipment that is currently In use.');
    }

    try {
      await axios.delete(`/api/v1/equipment/${equipmentId}`);
      await fetchEquipment();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to delete equipment.';
      throw new Error(detail);
    }
  }

  const activeRentals = computed(() => rentals.value.filter((rental) => !rental.returnedAt));

  const openRentalsForCurrentUser = computed(() => {
    if (!authStore.currentUser) {
      return [];
    }
    return rentals.value.filter((rental) => rental.userId === authStore.currentUser.id && !rental.returnedAt);
  });

  const equipmentForCurrentUser = computed(() => {
    if (!authStore.currentUser) {
      return [];
    }

    if (authStore.currentUser.isAdmin) {
      return equipment.value;
    }

    return equipment.value.filter((item) => item.status !== 'Error');
  });

  const dashboardStats = computed(() => {
    const total = equipment.value.length;
    const available = equipment.value.filter((item) => item.status === 'Available').length;
    const inUse = equipment.value.filter((item) => item.status === 'In use').length;
    const repair = equipment.value.filter((item) => item.status === 'Repair').length;

    return [
      { label: 'Total equipment', value: String(total), hint: 'All tracked hardware' },
      { label: 'Available', value: String(available), hint: 'Ready to rent' },
      { label: 'In use', value: String(inUse), hint: 'Currently assigned' },
      { label: 'Repair', value: String(repair), hint: 'Needs attention' },
    ];
  });

  function buildAuditReport() {
    const longestRepair = equipment.value
      .filter((item) => item.status === 'Repair')
      .map((item) => {
        const startTime = new Date(item.purchaseDate || '2026-02-05T00:00:00Z');
        const days = Math.max(1, Math.round((Date.now() - startTime.getTime()) / 86_400_000));
        return {
          item,
          days,
        };
      })
      .sort((left, right) => right.days - left.days);

    const neverRented = equipment.value.filter((item) => !rentals.value.some((rental) => rental.equipmentId === item.id));
    const highFrequency = equipment.value
      .map((item) => ({
        item,
        count: rentals.value.filter((rental) => rental.equipmentId === item.id).length,
      }))
      .filter((entry) => entry.count >= 2)
      .sort((left, right) => right.count - left.count);

    const report = {
      generatedAt: new Date().toISOString(),
      summary: [
        `Inventory snapshot: ${equipment.value.length} assets, ${activeRentals.value.length} open rentals.`,
        `${longestRepair.length} items currently sit in Repair, ${neverRented.length} have never been rented.`,
      ],
      findings: [
        ...longestRepair.slice(0, 3).map((entry) => ({
          label: entry.item.name,
          detail: `${entry.days} days in Repair`,
          severity: 'High',
        })),
        ...neverRented.slice(0, 3).map((item) => ({
          label: item.name,
          detail: 'No rental history yet',
          severity: 'Medium',
        })),
        ...highFrequency.slice(0, 3).map((entry) => ({
          label: entry.item.name,
          detail: `${entry.count} recorded rentals`,
          severity: 'Watch',
        })),
      ],
    };

    auditReport.value = report;
    return report;
  }

  async function resetDatabase() {
    try {
      await axios.post('/api/v1/users/reset-db');
      await fetchData();
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to reset database.';
      throw new Error(detail);
    }
  }

  return {
    equipment,
    rentals,
    auditReport,
    activeRentals,
    openRentalsForCurrentUser,
    equipmentForCurrentUser,
    dashboardStats,
    rentEquipment,
    returnRental,
    toggleRepairStatus,
    saveEquipment,
    createEquipmentItem,
    deleteEquipmentItem,
    buildAuditReport,
    getEquipmentById,
    getOpenRentalForEquipment,
    fetchEquipment,
    fetchRentals,
    fetchData,
    resetDatabase,
  };
});
