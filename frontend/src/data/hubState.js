import { computed, ref } from 'vue';

const SESSION_KEY = 'hardware-hub-session';

const userDirectory = [
  { id: 1, username: 'admin', password: 'admin', displayName: 'Alex Morgan', isAdmin: true },
  { id: 2, username: 'user', password: 'user', displayName: 'Jordan Lee', isAdmin: false },
];

const initialEquipment = [
  { id: 1, name: 'MacBook Pro 16"', brand: 'Apple', serialNumber: 'MBP-2024-001', purchaseDate: '2026-01-15', status: 'InUse' },
  { id: 2, name: 'Dell XPS 15', brand: 'Dell', serialNumber: 'DELL-XPS-002', purchaseDate: '2026-01-20', status: 'InUse' },
  { id: 3, name: 'iPhone 15 Pro', brand: 'Apple', serialNumber: 'IPH-15-003', purchaseDate: '2026-02-01', status: 'Available' },
  { id: 4, name: 'iPad Air', brand: 'Apple', serialNumber: 'IPAD-AIR-004', purchaseDate: '2026-02-05', status: 'Repair' },
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

const equipment = ref(initialEquipment.map((item) => ({ ...item })));
const rentals = ref(initialRentals.map((item) => ({ ...item })));
const auditReport = ref(null);
const session = ref(readSession());

function readSession() {
  if (typeof window === 'undefined') {
    return null;
  }

  try {
    const stored = window.localStorage.getItem(SESSION_KEY);
    return stored ? JSON.parse(stored) : null;
  } catch {
    return null;
  }
}

function persistSession(value) {
  if (typeof window === 'undefined') {
    return;
  }

  if (value) {
    window.localStorage.setItem(SESSION_KEY, JSON.stringify(value));
  } else {
    window.localStorage.removeItem(SESSION_KEY);
  }
}

function getEquipmentById(id) {
  return equipment.value.find((item) => item.id === Number(id));
}

function getOpenRentalForEquipment(equipmentId) {
  return rentals.value.find((rental) => rental.equipmentId === Number(equipmentId) && !rental.returnedAt);
}

function login(username, password) {
  const user = userDirectory.find((entry) => entry.username.toLowerCase() === username.trim().toLowerCase() && entry.password === password);

  if (!user) {
    throw new Error('Invalid credentials. Use admin / admin or user / user.');
  }

  const payload = {
    id: user.id,
    username: user.username,
    displayName: user.displayName,
    isAdmin: user.isAdmin,
  };

  session.value = payload;
  persistSession(payload);
  return payload;
}

function logout() {
  session.value = null;
  persistSession(null);
}

function rentEquipment(equipmentId) {
  if (!currentUser.value) {
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
    userId: currentUser.value.id,
    rentedAt: new Date().toISOString(),
    returnedAt: null,
  });
}

function returnRental(rentalId) {
  if (!currentUser.value) {
    throw new Error('You must be logged in to return equipment.');
  }

  const rental = rentals.value.find((entry) => entry.id === Number(rentalId));

  if (!rental || rental.returnedAt) {
    throw new Error('No open rental found for that record.');
  }

  if (rental.userId !== currentUser.value.id && !currentUser.value.isAdmin) {
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

  item.status = item.status === 'Repair' ? 'Available' : 'Repair';
}

function saveEquipment(equipmentId, patch) {
  const item = getEquipmentById(equipmentId);

  if (!item) {
    throw new Error('Equipment not found.');
  }

  if (patch.status === 'Repair' && item.status === 'InUse') {
    throw new Error('Cannot set an item to Repair while it is InUse.');
  }

  Object.assign(item, {
    ...patch,
    purchaseDate: patch.purchaseDate ? patch.purchaseDate.slice(0, 10) : item.purchaseDate,
  });
}

function createEquipmentItem(payload) {
  const nextId = Math.max(...equipment.value.map((item) => item.id), 0) + 1;
  equipment.value.unshift({
    id: nextId,
    name: payload.name.trim(),
    brand: payload.brand.trim(),
    serialNumber: payload.serialNumber.trim(),
    purchaseDate: payload.purchaseDate,
    status: payload.status,
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

const currentUser = computed(() => {
  if (!session.value) {
    return null;
  }

  return session.value;
});

const isAuthenticated = computed(() => Boolean(currentUser.value));

const activeRentals = computed(() => rentals.value.filter((rental) => !rental.returnedAt));

const openRentalsForCurrentUser = computed(() => {
  if (!currentUser.value) {
    return [];
  }

  return rentals.value.filter((rental) => !rental.returnedAt && (currentUser.value.isAdmin || rental.userId === currentUser.value.id));
});

const equipmentForCurrentUser = computed(() => {
  if (!currentUser.value) {
    return [];
  }

  if (currentUser.value.isAdmin) {
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
    .map((item) => ({
      item,
      days: Math.max(1, Math.round((Date.now() - new Date('2026-02-05T00:00:00Z').getTime()) / 86_400_000)),
    }))
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
  return {
    currentUser,
    isAuthenticated,
    equipment,
    rentals,
    auditReport,
    activeRentals,
    openRentalsForCurrentUser,
    equipmentForCurrentUser,
    dashboardStats,
    login,
    logout,
    rentEquipment,
    returnRental,
    toggleRepairStatus,
    saveEquipment,
    createEquipmentItem,
    deleteEquipmentItem,
    buildAuditReport,
    getEquipmentById,
    getOpenRentalForEquipment,
    cloneEquipmentItem,
    formatDate,
    formatDateTime,
    userDirectory,
    toIsoDate,
  };
}
