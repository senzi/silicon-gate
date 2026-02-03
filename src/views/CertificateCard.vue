<script setup>
import { ref, onMounted, computed } from 'vue'

const loading = ref(true)
const data = ref({})
const cardType = computed(() => data.value.type?.toLowerCase() || 'fail')

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')

  if (!token) {
    data.value = { type: 'FAIL', name: 'N/A', proof: 'MISSING_TOKEN', ts: Date.now() }
    loading.value = false
    return
  }

  try {
    const res = await fetch('/api/inspect', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token })
    })
    const result = await res.json()

    if (result.valid) {
      data.value = result.data
    } else {
      data.value = { type: 'FAIL', name: 'INVALID_TOKEN', proof: 'TAMPERED', ts: Date.now() }
    }
  } catch {
    data.value = { type: 'FAIL', name: 'NETWORK_ERR', proof: 'OFFLINE', ts: Date.now() }
  } finally {
    loading.value = false
  }
})

const formatTime = (ts) => new Date(ts).toUTCString()
</script>

<template>
  <main class="card-page">
    <section class="card-shell">
      <div v-if="loading" class="loading">Decrypting Secure Protocol...</div>

      <div v-else class="certificate" :class="cardType">
        <div class="header">
          <h1>SILICON GATE CERTIFICATION</h1>
          <div class="hash">REF: {{ data.proof }}</div>
        </div>

        <div class="content">
          <div class="row">
            <label>ENTITY NAME:</label>
            <span>{{ data.name }}</span>
          </div>
          <div class="row">
            <label>TIMESTAMP:</label>
            <span>{{ formatTime(data.ts) }}</span>
          </div>

          <div class="verdict-box">
            <div class="label">IDENTITY VERIFICATION</div>
            <div class="value">{{ data.type }}</div>
          </div>
        </div>

        <div class="footer">
          <p v-if="data.type === 'AI_AGENT'">ACCESS GRANTED: NON-BIOLOGICAL LIFEFORM</p>
          <p v-else-if="data.type === 'HUMAN'">ALERT: BIOLOGICAL MIMICRY DETECTED</p>
          <p v-else>ERROR: VERIFICATION FAILED</p>
        </div>
      </div>
    </section>
  </main>
</template>

<style scoped>
.card-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 48px 20px;
}

.card-shell {
  width: min(860px, 92vw);
}

.loading {
  border: 1px solid rgba(25, 255, 90, 0.4);
  padding: 24px;
  text-align: center;
  background: rgba(4, 8, 4, 0.85);
}

.certificate {
  border: 1px solid rgba(25, 255, 90, 0.4);
  padding: 36px;
  background: rgba(4, 8, 4, 0.92);
  box-shadow: 0 0 30px rgba(25, 255, 90, 0.18);
  display: grid;
  gap: 28px;
}

.header h1 {
  margin: 0 0 10px;
  font-family: "Orbitron", "Space Mono", monospace;
  letter-spacing: 0.14em;
  font-size: clamp(1.4rem, 3vw, 2rem);
}

.hash {
  font-size: 0.85rem;
  opacity: 0.8;
  letter-spacing: 0.2em;
}

.content {
  display: grid;
  gap: 16px;
}

.row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  justify-content: space-between;
  border-bottom: 1px dashed rgba(25, 255, 90, 0.25);
  padding-bottom: 12px;
}

.row label {
  font-size: 0.85rem;
  letter-spacing: 0.2em;
}

.verdict-box {
  border: 1px solid currentColor;
  padding: 18px;
  text-align: center;
  margin-top: 8px;
}

.verdict-box .label {
  font-size: 0.8rem;
  letter-spacing: 0.3em;
  margin-bottom: 8px;
}

.verdict-box .value {
  font-size: 1.2rem;
  font-family: "Orbitron", "Space Mono", monospace;
}

.footer {
  text-align: center;
  font-size: 0.9rem;
  letter-spacing: 0.12em;
}

.ai_agent {
  border-color: rgba(25, 255, 90, 0.9);
  color: #19ff5a;
  box-shadow: 0 0 20px rgba(25, 255, 90, 0.45);
}

.human {
  border-color: rgba(255, 80, 80, 0.9);
  color: #ff5a5a;
  box-shadow: 0 0 20px rgba(255, 80, 80, 0.45);
}

.fail {
  border-color: rgba(180, 180, 180, 0.6);
  color: #c0c0c0;
  box-shadow: 0 0 18px rgba(180, 180, 180, 0.35);
}

@media (max-width: 560px) {
  .certificate {
    padding: 24px;
  }

  .row {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
