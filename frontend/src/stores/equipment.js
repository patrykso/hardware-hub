import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { useAuthStore } from './auth';

const initialEquipment = [
  { id: 1, name: 'MacBook Pro 16"', brand: 'Apple', serialNumber: 'MBP-2024-001', purchaseDate: '2026-01-15', status: 'InUse' },
  { id: 2, name: 'Dell XPS 15', brand: 'Dell', serialNumber: 'DELL-XPS-002', purchaseDate: '2026-01-20', status: 'InUse' },
  { id: 3, name: 'iPhone 15 Pro', brand: 'Apple', serialNumber: 'IPH-15-003', purchaseDate: '2026-02-01', status: 'Available' },
  { id: 4, name: 'iPad Air', brand: 'Apple', serialNumber: 'IPAD-AIR-004', purchaseDate: '2026-02-05', status: 'Repair', repairStartedAt: '2026-02-05T00:00:00Z' },
  { id: 5, name: 'ThinkPad X1 Carbon', brand: 'Lenovo', serialNumber: 'TPX1-005', purchaseDate: '2026-02-10', status: 'Available' },
  { id: 6, name: 'Surface Pro 9', brand: 'Microsoft', serialNumber: 'SRF-PRO-006', purchaseDate: '2026-02-12', status: 'InUse' },
  { id: 7, name: 'Magic Keyboard', brand: 'Apple', serialNumber: 'MKB-007', purchaseDate: '2026-02-15', status: 'Available' },
  { id: 8, name: 'Logitech MX Master 3S', brand: 'Logitech', serialNumber: 'MXM-3S-008', purchaseDate: '2026-02-18', status: 'Available' },
  { id: 9, name: 'MacBook Air M2', brand: 'Apple', serialNumber: 'MBA-M2-009', purchaseDate: '2026-02-22', status: 'Available' },
  { id: 10, name: 'Sony WH-1000XM5', brand: 'Sony', serialNumber: 'SONY-010', purchaseDate: '2026-02-25', status: 'Available' },
  { id: 11, name: 'Samsung Galaxy Tab S9', brand: 'Samsung', serialNumber: 'TAB-S9-011', purchaseDate: '2026-03-01', status: 'Available' },
];

const initialRentals = [
  { id: 1, equipmentId: 1, userId: 2, rentedAt: '2026-05-12T09:30:00Z', returnedAt: null },
  { id: 2, equipmentId: 2, userId: 1, rentedAt: '2026-05-20T13:00:00Z', returnedAt: null },
  { id: 3, equipmentId: 6, userId: 1, rentedAt: '2026-05-01T08:00:00Z', returnedAt: null },
  { id: 4, equipmentId: 3, userId: 2, rentedAt: '2026-04-18T11:00:00Z', returnedAt: '2026-04-25T16:30:00Z' },
];

export const useEquipmentStore = defineStore('equipment', () => {
  const authStore = useAuthStore();

  const equipment = ref(initialEquipment.map((item) => ({ ...item })));
  const rentals = ref(initialRentals.map((item) => ({ ...item })));
  const auditReport = ref(null);

  function getEquipmentById(id) {
    return equipment.value.find((item) => item.id === Number(id));
  }

  function getOpenRentalForEquipment(equipmentId) {
    return rentals.value.find((rental) => rental.equipmentId === Number(equipmentId) && !rental.returnedAt);
  }

  function rentEquipment(equipmentId) {
    if (!authStore.currentUser) {
      throw new Error('You must be logged in to rent equipment.');
    }

    const item = getEquipmentById(equipmentId);

    if (!item) {
      throw new Error('Equipment not found.');
    }

    if (item.status !== 'Available') {
      throw new Error('Cannot rent equipment unless it is Available.');
    }

    if (getOpenRentalForEquipment(item.id)) {
      throw new Error('This equipment already has an open rental.');
    }

    item.status = 'InUse';
    rentals.value.unshift({
      id: rentals.value.length + 1,
      equipmentId: item.id,
      userId: authStore.currentUser.id,
      rentedAt: new Date().toISOString(),
      returnedAt: null,
    });
  }

  function returnRental(rentalId) {
    if (!authStore.currentUser) {
      throw new Error('You must be logged in to return equipment.');
    }

    const rental = rentals.value.find((entry) => entry.id === Number(rentalId));

    if (!rental || rental.returnedAt) {
      throw new Error('No open rental found for that record.');
    }

    if (rental.userId !== authStore.currentUser.id && !authStore.currentUser.isAdmin) {
      throw new Error('You cannot return equipment rented by another user.');
    }

    const item = getEquipmentById(rental.equipmentId);
    if (item) {
      item.status = 'Available';
    }

    rental.returnedAt = new Date().toISOString();
  }

  function toggleRepairStatus(equipmentId) {
    const item = getEquipmentById(equipmentId);

    if (!item) {
      throw new Error('Equipment not found.');
    }

    if (item.status === 'InUse') {
      throw new Error('Equipment in use must be returned before it can be moved to Repair.');
    }

    if (item.status === 'Repair') {
      item.status = 'Available';
      item.repairStartedAt = null;
    } else {
      item.status = 'Repair';
      item.repairStartedAt = new Date().toISOString();
    }
  }

  function saveEquipment(equipmentId, patch) {
    const item = getEquipmentById(equipmentId);

    if (!item) {
      throw new Error('Equipment not found.');
    }

    // Copilot Comment 1 Fix: Block direct status changes away from InUse while an open rental exists
    const openRental = getOpenRentalForEquipment(equipmentId);
    if (openRental && patch.status && patch.status !== 'InUse') {
      throw new Error('Equipment currently in use cannot be moved away from InUse status without returning it first.');
    }

    if (patch.status === 'Repair' && item.status === 'InUse') {
      throw new Error('Cannot set an item to Repair while it is InUse.');
    }

    // Copilot Comment 2 Fix: Track a repair-start timestamp per item (set when moving to Repair, clear when leaving)
    if (patch.status === 'Repair' && item.status !== 'Repair') {
      item.repairStartedAt = new Date().toISOString();
    } else if (patch.status && patch.status !== 'Repair') {
      item.repairStartedAt = null;
    }

    Object.assign(item, {
      ...patch,
      purchaseDate: patch.purchaseDate ? patch.purchaseDate.slice(0, 10) : item.purchaseDate,
    });
  }

  function createEquipmentItem(payload) {
    const nextId = Math.max(...equipment.value.map((item) => item.id), 0) + 1;
    const isRepair = payload.status === 'Repair';
    equipment.value.unshift({
      id: nextId,
      name: payload.name.trim(),
      brand: payload.brand.trim(),
      serialNumber: payload.serialNumber.trim(),
      purchaseDate: payload.purchaseDate,
      status: payload.status,
      repairStartedAt: isRepair ? new Date().toISOString() : null,
    });
  }

  function deleteEquipmentItem(equipmentId) {
    const item = getEquipmentById(equipmentId);

    if (!item) {
      throw new Error('Equipment not found.');
    }

    if (item.status === 'InUse') {
      throw new Error('Cannot delete equipment that is currently InUse.');
    }

    equipment.value = equipment.value.filter((entry) => entry.id !== Number(equipmentId));
    rentals.value = rentals.value.filter((entry) => entry.equipmentId !== Number(equipmentId));
  }

  const activeRentals = computed(() => rentals.value.filter((rental) => !rental.returnedAt));

  const openRentalsForCurrentUser = computed(() => {
    if (!authStore.currentUser) {
      return [];
    }

    return rentals.value.filter((rental) => !rental.returnedAt && (authStore.currentUser.isAdmin || rental.userId === authStore.currentUser.id));
  });

  const equipmentForCurrentUser = computed(() => {
    if (!authStore.currentUser) {
      return [];
    }

    if (authStore.currentUser.isAdmin) {
      return equipment.value;
    }

    return equipment.value.filter((item) => item.status !== 'Repair' || item.id === 4 || item.status === 'Available' || item.status === 'InUse');
  });

  const dashboardStats = computed(() => {
    const total = equipment.value.length;
    const available = equipment.value.filter((item) => item.status === 'Available').length;
    const inUse = equipment.value.filter((item) => item.status === 'InUse').length;
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
        // Copilot Comment 2 Fix: Track a repair-start timestamp per item and use it when building the audit report
        const startTime = item.repairStartedAt ? new Date(item.repairStartedAt) : new Date(item.purchaseDate || '2026-02-05T00:00:00Z');
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
  };
});
