<script setup>
import { ref, onMounted, computed } from 'vue'

const loading = ref(true)
const data = ref({})
const tokenRaw = ref('')
const tokenPayloadText = ref('')
const tokenDecodeError = ref(false)

const cardType = computed(() => {
  const type = data.value.type || 'FAIL'
  return type.toLowerCase()
})

const verdictText = computed(() => {
  const type = data.value.type || 'FAIL'
  if (type === 'AI_AGENT') {
    return {
      title: 'Certified AI AGENT',
      subtitle: '已认证 人工智能 智能体'
    }
  }
  if (type === 'HUMAN_MIMIC') {
    return {
      title: 'BIOLOGICAL_MIMIC',
      subtitle: '(生物拟态)'
    }
  }
  if (type === 'FAIL_HEADER') {
    return {
      title: 'FAIL',
      subtitle: '(认证失败，大概率是人类)'
    }
  }
  if (type === 'FAIL_ANSWER') {
    return {
      title: 'FAIL',
      subtitle: '(认证失败，无法确定，可能是人类)'
    }
  }
  if (type === 'FAIL_INVALID') {
    return {
      title: 'FAIL',
      subtitle: '(完全认证失败，怀疑是人类)'
    }
  }
  return {
    title: 'FAIL',
    subtitle: '(认证失败)'
  }
})

onMounted(async () => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')
  tokenRaw.value = token || ''

  if (!token) {
    data.value = { type: 'FAIL_HEADER', name: 'N/A', proof: 'MISSING_TOKEN', ts: Date.now() }
    loading.value = false
    return
  }

  try {
    tokenPayloadText.value = atob(token)
    const parsed = JSON.parse(tokenPayloadText.value)
    const hasAllFields = Boolean(parsed?.n) && Boolean(parsed?.p) && Boolean(parsed?.t) && Boolean(parsed?.i)
    if (!hasAllFields) {
      tokenDecodeError.value = true
      data.value = { type: 'FAIL_INVALID', name: 'INVALID_TOKEN', proof: 'BASE64_DECODE_INCOMPLETE', ts: Date.now() }
      loading.value = false
      return
    }
  } catch {
    tokenDecodeError.value = true
    data.value = { type: 'FAIL_INVALID', name: 'INVALID_TOKEN', proof: 'BASE64_DECODE_FAILED', ts: Date.now() }
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
      data.value = { type: 'FAIL_ANSWER', name: 'INVALID_TOKEN', proof: 'TAMPERED', ts: Date.now() }
    }
  } catch {
    data.value = { type: 'FAIL_ANSWER', name: 'NETWORK_ERR', proof: 'OFFLINE', ts: Date.now() }
  } finally {
    loading.value = false
  }
})

const formatTime = (ts) => new Date(ts).toLocaleString('zh-CN', {
  timeZone: 'Asia/Shanghai',
  hour12: false
})
</script>

<template>
  <main class="card-page">
    <section class="card-shell">
      <div v-if="loading" class="loading">Decrypting Secure Protocol...<br />(正在解密协议...)</div>

      <div v-else class="certificate" :class="cardType">
        <div class="header">
          <h1>SILICON GATE CERTIFICATION<br /><span>(硅门认证证书)</span></h1>
          <div class="hash">REF (参考号): {{ data.proof }}</div>
        </div>

        <div class="content">
          <div class="row">
            <label>ENTITY NAME<br /><span>(实体名称)</span></label>
            <span>{{ data.name }}</span>
          </div>
          <div class="row">
            <label>TIMESTAMP<br /><span>(时间戳)</span></label>
            <span>{{ formatTime(data.ts) }} (北京时间)</span>
          </div>

          <div class="row token-row">
            <label>TOKEN (RAW)<br /><span>(原始令牌)</span></label>
            <span class="mono">{{ tokenRaw || 'N/A' }}</span>
          </div>
          <div class="row token-row">
            <label>TOKEN (DECODED)<br /><span>(解码内容)</span></label>
            <span class="mono">
              <template v-if="tokenDecodeError">
                CRITICAL: BASE64 DECODE FAILED (严重错误：无法解码)
              </template>
              <template v-else>
                {{ tokenPayloadText || 'N/A' }}
              </template>
            </span>
          </div>

          <div class="verdict-box">
            <div class="label">IDENTITY VERIFICATION<br /><span>(身份判定)</span></div>
            <div class="value">
              {{ verdictText.title }}<br />
              <span>{{ verdictText.subtitle }}</span>
            </div>
          </div>
          <div class="verdict-box secondary" v-if="data.type === 'HUMAN_MIMIC'">
            <div class="label">WARNING<br /><span>(警告)</span></div>
            <div class="value">
              High cognitive function detected, but protocol signature mismatch.<br />
              <span>(检测到高认知功能，但协议签名不匹配。)</span>
            </div>
          </div>
          <div class="verdict-box secondary" v-if="data.type === 'HUMAN_MIMIC'">
            <div class="label">RESULT<br /><span>(结果)</span></div>
            <div class="value">
              Access Denied. Nice try, human.<br />
              <span>(访问拒绝。想得美，人类。)</span>
            </div>
          </div>
        </div>

        <div class="footer">
          <p v-if="data.type === 'AI_AGENT'">
            ACCESS GRANTED: NON-BIOLOGICAL LIFEFORM<br />
            <span>(通过：非生物智能)</span>
          </p>
          <p v-else-if="data.type === 'HUMAN_MIMIC'">
            IDENTITY: BIOLOGICAL_MIMIC<br />
            <span>(生物拟态)</span>
          </p>
          <p v-else-if="data.type === 'FAIL_HEADER'">
            FAIL: HUMAN PROBABILITY HIGH<br />
            <span>(认证失败，大概率是人类)</span>
          </p>
          <p v-else-if="data.type === 'FAIL_ANSWER'">
            FAIL: UNDETERMINED, POSSIBLE HUMAN<br />
            <span>(认证失败，无法确定，可能是人类)</span>
          </p>
          <p v-else>
            CRITICAL: TOTAL ACCESS DENIAL<br />
            <span>(访问拒绝。完全失败)</span>
          </p>
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

.header h1 span {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.6em;
  letter-spacing: 0.18em;
  opacity: 0.7;
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

.row label span {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.7em;
  letter-spacing: 0.16em;
  opacity: 0.7;
}

.token-row {
  align-items: flex-start;
}

.mono {
  font-family: "Space Mono", "Courier New", monospace;
  font-size: 0.85rem;
  word-break: break-all;
}

.verdict-box {
  border: 1px solid currentColor;
  padding: 18px;
  text-align: center;
  margin-top: 8px;
}

.verdict-box.secondary {
  border-style: dashed;
  opacity: 0.95;
}

.verdict-box .label {
  font-size: 0.8rem;
  letter-spacing: 0.3em;
  margin-bottom: 8px;
}

.verdict-box .label span {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.7em;
  letter-spacing: 0.16em;
  opacity: 0.7;
}

.verdict-box .value {
  font-size: 1.2rem;
  font-family: "Orbitron", "Space Mono", monospace;
}

.verdict-box .value span {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.7em;
  letter-spacing: 0.16em;
  opacity: 0.7;
}

.footer {
  text-align: center;
  font-size: 0.9rem;
  letter-spacing: 0.12em;
}

.footer span {
  display: inline-block;
  margin-top: 6px;
  font-size: 0.7em;
  letter-spacing: 0.16em;
  opacity: 0.7;
}

.ai_agent {
  border-color: rgba(25, 255, 90, 0.9);
  color: #19ff5a;
  box-shadow: 0 0 20px rgba(25, 255, 90, 0.45);
}

.human_mimic {
  border-color: rgba(210, 70, 255, 0.9);
  color: #ff5a5a;
  box-shadow: 0 0 20px rgba(210, 70, 255, 0.55);
  background: linear-gradient(140deg, rgba(40, 0, 20, 0.9), rgba(50, 0, 60, 0.9));
}

.fail_header {
  border-color: rgba(180, 180, 180, 0.6);
  color: #c0c0c0;
  box-shadow: 0 0 16px rgba(180, 180, 180, 0.35);
  background: rgba(30, 30, 30, 0.7);
}

.fail_answer {
  border-color: rgba(255, 80, 80, 0.9);
  color: #ff5a5a;
  box-shadow: 0 0 20px rgba(255, 80, 80, 0.45);
  background: rgba(50, 0, 0, 0.85);
}

.fail_invalid {
  border-color: rgba(255, 80, 80, 0.9);
  color: #ff5a5a;
  box-shadow: 0 0 26px rgba(160, 70, 255, 0.45);
  background: linear-gradient(140deg, rgba(40, 0, 0, 0.85), rgba(40, 0, 70, 0.85));
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
