import { createRouter, createWebHistory } from "vue-router";
import { useHubState } from "./data/hubState";
import LoginView from "./views/LoginView.vue";
import HardwareListView from "./views/HardwareListView.vue";
import MyRentalsView from "./views/MyRentalsView.vue";
import AdminPanelView from "./views/AdminPanelView.vue";
import EditEquipmentView from "./views/EditEquipmentView.vue";
import UsersView from "./views/UsersView.vue";
import AuditView from "./views/AuditView.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", component: LoginView, meta: { public: true } },
  {
    path: "/hardware",
    component: HardwareListView,
    meta: { title: "Hardware List" },
  },
  { path: "/rentals", component: MyRentalsView, meta: { title: "My Rentals" } },
  {
    path: "/admin",
    component: AdminPanelView,
    meta: { title: "Admin Panel", adminOnly: true },
  },
  {
    path: "/admin/equipment/:id",
    component: EditEquipmentView,
    meta: { title: "Edit Equipment", adminOnly: true },
  },
  {
    path: "/users",
    component: UsersView,
    meta: { title: "User Accounts", adminOnly: true },
  },
  {
    path: "/audit",
    component: AuditView,
    meta: { title: "AI Assistant Audit", adminOnly: true },
  },
  { path: "/:pathMatch(.*)*", redirect: "/hardware" },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 };
  },
});

router.beforeEach(async (to) => {
  const hub = useHubState();

  if (to.meta.public) {
    return true;
  }

  if (!hub.isAuthenticated.value) {
    return { path: "/login", query: { redirect: to.fullPath } };
  }

  if (to.meta.adminOnly && !hub.currentUser.value?.isAdmin) {
    return { path: "/hardware" };
  }

  try {
    await hub.fetchData();
    if (hub.currentUser.value?.isAdmin) {
      await hub.fetchUsers();
    }
  } catch (err) {
    console.error("Failed to pre-fetch data:", err);
  }

  return true;
});

export default router;
