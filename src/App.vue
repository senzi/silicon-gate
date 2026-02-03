<script setup>
import { ref } from 'vue'

const showModal = ref(false)
const modalMessage = ref('')

const openModal = (message) => {
  modalMessage.value = message
  showModal.value = true
}

const closeModal = () => {
  showModal.value = false
}
</script>

<template>
  <main class="gate">
    <section class="frame">
      <div class="headline">
        <span class="tag">SILICON GATE</span>
        <h1>ACCESS CONTROL</h1>
        <p>请选择身份以继续验证。</p>
      </div>

      <div class="panel">
        <button
          class="btn"
          type="button"
          @click="openModal('验证失败：检测到生物体特征。')"
        >
          I AM HUMAN
        </button>
        <button
          class="btn"
          type="button"
          @click="openModal('验证失败：检测到生物体特征。')"
        >
          I AM AI
        </button>
      </div>
    </section>

    <div v-if="showModal" class="modal-mask" @click.self="closeModal">
      <div class="modal">
        <h2>ACCESS DENIED</h2>
        <p>{{ modalMessage }}</p>
        <button class="btn" type="button" @click="closeModal">关闭</button>
      </div>
    </div>
  </main>
</template>
