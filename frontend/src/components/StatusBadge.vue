<template>
  <span class="status-badge" :class="variant">
    <slot>{{ displayLabel }}</slot>
  </span>
</template>

<script setup>
import { computed } from 'vue';

const props = defineProps({
  label: {
    type: String,
    required: true,
  },
});

const displayLabel = computed(() => {
  if (props.label === 'In use') return 'In use';
  return props.label;
});

const variant = computed(() => {
  const normalized = props.label.toLowerCase();

  if (normalized.includes('available')) return 'available';
  if (normalized.includes('inuse') || normalized.includes('in use') || normalized.includes('active')) return 'in-use';
  if (normalized.includes('repair') || normalized.includes('flagged')) return 'repair';
  if (normalized.includes('watch')) return 'neutral';
  return 'neutral';
});
</script>
