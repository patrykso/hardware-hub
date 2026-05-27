<template>
  <article class="stat-card">
    <p>{{ label }}</p>
    <strong>{{ value }}</strong>
    <span>{{ hint }}</span>
  </article>
</template>

<script setup>
defineProps({
  label: { type: String, required: true },
  value: { type: String, required: true },
  hint: { type: String, required: true },
});
</script>
