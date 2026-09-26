<script setup>
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()

function sair() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="dashboard">
    <h1>Bem-vindo!</h1>
    <p>Login funcionando. Telas futura vão aqui!.</p>
    <button @click="sair">Sair</button>
  </div>
</template>

<style scoped>
.dashboard {
  padding: 1.5rem;
  padding-top: calc(1.5rem + env(safe-area-inset-top, 0px));
}
</style>
