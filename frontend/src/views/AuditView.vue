<template>
  <AppShell>
    <section class="audit-grid">
      <div class="surface-card audit-panel">
        <div class="audit-header">
          <div>
            <p class="eyebrow">Hardware Manager</p>
            <h2>AI Assistant Audit</h2>
            <p>Run an inventory health check and review the generated findings here.</p>
          </div>

          <button class="primary-button" type="button" @click="runAudit">Run Audit</button>
        </div>

        <div v-if="report" class="audit-report">
          <div class="audit-summary">
            <p v-for="line in report.summary" :key="line">{{ line }}</p>
          </div>

          <div class="audit-findings">
            <article v-for="finding in report.findings" :key="`${finding.label}-${finding.detail}`" class="finding-card">
              <StatusBadge :label="finding.severity" />
              <div>
                <strong>{{ finding.label }}</strong>
                <p>{{ finding.detail }}</p>
              </div>
            </article>
          </div>
        </div>
      </div>

      <aside class="surface-card audit-sidebar">
        <h3>Suggested Queries</h3>
        <button v-for="prompt in prompts" :key="prompt.title" class="suggestion-card" type="button" @click="seedPrompt(prompt.query)">
          <span class="material-symbols-outlined">{{ prompt.icon }}</span>
          <div>
            <strong>{{ prompt.title }}</strong>
            <p>{{ prompt.query }}</p>
          </div>
        </button>
      </aside>
    </section>
  </AppShell>
</template>

<script setup>
import { computed } from 'vue';
import AppShell from '../components/AppShell.vue';
import StatusBadge from '../components/StatusBadge.vue';
import { useHubState } from '../data/hubState';

const hub = useHubState();
const prompts = [
  { title: 'Inventory Health', query: 'Show me laptops with battery health below 60%', icon: 'monitoring' },
  { title: 'Lease Renewals', query: 'Which MacBook rentals expire next month?', icon: 'schedule' },
  { title: 'Cost Analysis', query: 'Summarize repair costs for Q3 across all departments', icon: 'paid' },
];

const report = computed(() => hub.auditReport.value);

function runAudit() {
  hub.buildAuditReport();
}

function seedPrompt(prompt) {
  window.alert(`Demo prompt: ${prompt}`);
}
</script>
