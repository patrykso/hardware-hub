<template>
  <div class="auth-screen">
    <section class="auth-card">
      <div class="auth-mark">
        <span class="material-symbols-outlined filled">inventory_2</span>
      </div>

      <h1>Welcome back</h1>
      <p>Sign in to your account.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          <span>Email</span>
          <input
            v-model="form.username"
            type="text"
            placeholder="name@booksy.com"
            required
          />
        </label>

        <label>
          <span>Password</span>
          <input
            v-model="form.password"
            type="password"
            placeholder="Enter your password"
            required
          />
        </label>

        <button class="primary-button" type="submit">Login</button>
      </form>

      <div class="auth-hint">
        <strong>Demo credentials</strong>
        <p>Admin: admin / admin</p>
        <p>User: user / user</p>
      </div>

      <p v-if="error" class="form-error">{{ error }}</p>
    </section>
  </div>
</template>

<script setup>
import { reactive, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useHubState } from "../data/hubState";

const hub = useHubState();
const router = useRouter();
const route = useRoute();
const error = ref("");

const form = reactive({
  username: "",
  password: "",
});

async function submit() {
  error.value = "";

  try {
    const user = await hub.login(form.username, form.password);
    const target =
      route.query.redirect?.toString() ||
      (user.isAdmin ? "/admin" : "/hardware");
    router.push(target);
  } catch (exception) {
    error.value =
      exception instanceof Error ? exception.message : "Unable to log in.";
  }
}
</script>
