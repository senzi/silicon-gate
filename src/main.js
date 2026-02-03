import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import './style.css'
import App from './App.vue'
import GateView from './views/GateView.vue'
import CertificateCard from './views/CertificateCard.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: GateView },
    { path: '/card', component: CertificateCard }
  ]
})

createApp(App).use(router).mount('#app')
