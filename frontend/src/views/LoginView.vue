<template>
  <div class="auth-screen">
    <section class="auth-card">
      <div class="auth-mark">
        <span class="material-symbols-outlined filled">inventory_2</span>
      </div>

      <h1>Welcome back</h1>
      <p>Sign in to your Hardware Rental Hub workspace.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label>
          <span>Email</span>
          <input v-model="form.username" type="text" placeholder="admin" required />
        </label>

        <label>
          <span>Password</span>
          <input v-model="form.password" type="password" placeholder="admin" required />
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

    <aside class="auth-visual">
      <div class="auth-visual-copy">
        <p class="eyebrow">Precision Core</p>
        <h2>Track equipment, rentals, repairs, and audits in one interface.</h2>
        <p>The UI mirrors the Stitch layouts while staying fully interactive as a Vue SPA.</p>
      </div>

      <div class="auth-visual-grid">
        <div v-for="item in dashboardStats" :key="item.label" class="mini-stat">
          <span>{{ item.label }}</span>
          <strong>{{ item.value }}</strong>
        </div>
      </div>

      <div class="preview-stack">
        <article class="preview-card">
          <span class="material-symbols-outlined">search</span>
          <div>
            <strong>Hardware List</strong>
            <p>Search, sort, and filter inventory.</p>
          </div>
        </article>
        <article class="preview-card">
          <span class="material-symbols-outlined filled">smart_toy</span>
          <div>
            <strong>AI Audit</strong>
            <p>Generate a structured inventory report.</p>
          </div>
        </article>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, reactive, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useHubState } from '../data/hubState';

const hub = useHubState();
const router = useRouter();
const route = useRoute();
const error = ref('');
const dashboardStats = computed(() => hub.dashboardStats.value);

const form = reactive({
  username: 'user',
  password: 'user',
});

async function submit() {
  error.value = '';

  try {
    const user = await hub.login(form.username, form.password);
    const target = route.query.redirect?.toString() || (user.isAdmin ? '/admin' : '/hardware');
    router.push(target);
  } catch (exception) {
    error.value = exception instanceof Error ? exception.message : 'Unable to log in.';
  }
}

</script>
