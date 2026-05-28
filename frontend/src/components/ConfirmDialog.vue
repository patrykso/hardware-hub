<template>
  <Teleport to="body">
    <Transition name="dialog-fade">
      <div v-if="visible" class="dialog-overlay" @click.self="cancel">
        <div class="dialog-card" role="alertdialog" aria-modal="true">
          <div class="dialog-icon" :class="variant">
            <span class="material-symbols-outlined">{{ icon }}</span>
          </div>
          <h3 class="dialog-title">{{ title }}</h3>
          <p class="dialog-message">{{ message }}</p>
          <div class="dialog-actions">
            <button class="ghost-button" type="button" @click="cancel">
              Cancel
            </button>
            <button
              class="primary-button"
              :class="variant"
              type="button"
              @click="confirm"
            >
              {{ confirmLabel }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  title: { type: String, default: "Are you sure?" },
  message: { type: String, default: "" },
  confirmLabel: { type: String, default: "Confirm" },
  variant: { type: String, default: "danger" },
  icon: { type: String, default: "warning" },
});

const emit = defineEmits(["confirm", "cancel"]);

function confirm() {
  emit("confirm");
}

function cancel() {
  emit("cancel");
}
</script>
