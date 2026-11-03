
<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
import { RouterView } from 'vue-router'
</script>

<template>
  <div class="layout-principal">
    <AppSidebar />

    <main class="conteudo-principal">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.layout-principal {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
  background: var(--color-background, #F7F8FA);
}

.conteudo-principal {
  flex: 1;
  min-width: 0;
  min-height: 100vh;
  min-height: 100dvh;
}

@media (max-width: 850px) {
  .conteudo-principal {
    padding-top: 56px;
  }
}
</style>