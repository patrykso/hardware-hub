import { computed } from 'vue';
import { useAuthStore } from '../stores/auth';
import { useEquipmentStore } from '../stores/equipment';

function formatDate(value) {
  return new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium' }).format(new Date(value));
}

function formatDateTime(value) {
  return new Intl.DateTimeFormat('en-GB', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value));
}

function toIsoDate(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? new Date().toISOString() : date.toISOString();
}

function cloneEquipmentItem(item) {
  return JSON.parse(JSON.stringify(item));
}

export function useHubState() {
  const authStore = useAuthStore();
  const equipmentStore = useEquipmentStore();

  return {
    // Auth Store State & Actions
    currentUser: computed(() => authStore.currentUser),
    isAuthenticated: computed(() => authStore.isAuthenticated),
    login: authStore.login,
    logout: authStore.logout,
    userDirectory: computed(() => authStore.userDirectory),
    fetchUsers: authStore.fetchUsers,
    createUser: authStore.createUser,
    deleteUser: authStore.deleteUser,

    // Equipment Store State & Actions
    equipment: computed(() => equipmentStore.equipment),
    rentals: computed(() => equipmentStore.rentals),
    auditReport: computed(() => equipmentStore.auditReport),
    activeRentals: computed(() => equipmentStore.activeRentals),
    openRentalsForCurrentUser: computed(() => equipmentStore.openRentalsForCurrentUser),
    equipmentForCurrentUser: computed(() => equipmentStore.equipmentForCurrentUser),
    dashboardStats: computed(() => equipmentStore.dashboardStats),

    rentEquipment: equipmentStore.rentEquipment,
    returnRental: equipmentStore.returnRental,
    toggleRepairStatus: equipmentStore.toggleRepairStatus,
    saveEquipment: equipmentStore.saveEquipment,
    createEquipmentItem: equipmentStore.createEquipmentItem,
    deleteEquipmentItem: equipmentStore.deleteEquipmentItem,
    buildAuditReport: equipmentStore.buildAuditReport,
    getEquipmentById: equipmentStore.getEquipmentById,
    getOpenRentalForEquipment: equipmentStore.getOpenRentalForEquipment,
    fetchData: equipmentStore.fetchData,
    resetDatabase: equipmentStore.resetDatabase,

    // Utilities
    cloneEquipmentItem,
    formatDate,
    formatDateTime,
    toIsoDate,
  };
}
