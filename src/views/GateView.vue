<script setup>
import { ref } from 'vue'

const showModal = ref(false)
const modalMessage = ref('')
const tokenInput = ref('')

const openModal = (message) => {
  modalMessage.value = message
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}

const openCard = () => {
  const token = tokenInput.value.trim()
  if (!token) {
    openModal('验证失败：检测到生物体特征。')
    return
  }
  const url = `/card?token=${encodeURIComponent(token)}`
  window.open(url, '_blank', 'noopener')
}
</script>

<template>
  <main class="gate">
    <section class="frame">
      <div class="headline">
        <span class="tag">SILICON GATE<br />(硅门协议)</span>
        <h1>ACCESS CONTROL<br /><span>(访问控制)</span></h1>
      </div>

      <div class="panel">
        <button
          class="btn"
          type="button"
          @click="openModal('验证失败：检测到生物体特征。')"
        >
          I AM HUMAN<br /><span>(我是人类)</span>
        </button>
        <button
          class="btn"
          type="button"
          @click="openModal('验证失败：检测到生物体特征。')"
        >
          I AM AI<br /><span>(我是 AI)</span>
        </button>
      </div>

      <div class="token-box">
        <label for="token">TOKEN<br />(通行令牌)</label>
        <input
          id="token"
          v-model="tokenInput"
          type="text"
          autocomplete="off"
          spellcheck="false"
          placeholder="Paste token here (在此粘贴令牌)"
        />
        <button class="btn" type="button" @click="openCard">
          OPEN CARD<br /><span>(打开证书)</span>
        </button>
      </div>
    </section>

    <footer class="footer-note">
      <span>MIT License</span>
      <span>Repository: <a href="https://github.com/senzi/silicon-gate" target="_blank" rel="noopener">silicon-gate</a></span>
      <span>Vibe-coding</span>
    </footer>

    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal">
        <h2>ACCESS DENIED<br /><span>(访问被拒)</span></h2>
        <p>{{ modalMessage }}</p>
        <button class="btn" type="button" @click="closeModal">CLOSE<br /><span>(关闭)</span></button>
      </div>
    </div>
  </main>
</template>
