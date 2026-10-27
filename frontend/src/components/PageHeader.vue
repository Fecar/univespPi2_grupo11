
<script setup>
defineProps({
  categoria: {
    type: String,
    default: 'GESTÃO EDUCACIONAL'
  },
  titulo: {
    type: String,
    required: true
  },
  descricao: {
    type: String,
    default: ''
  },
  textoBotao: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['acao'])
</script>

<template>
  <header class="cabecalho-pagina">
    <div class="informacoes">
      <p class="categoria">{{ categoria }}</p>
      <h1>{{ titulo }}</h1>
      <p v-if="descricao" class="descricao">
        {{ descricao }}
      </p>
    </div>

    <button
      v-if="textoBotao"
      type="button"
      class="botao-principal"
      @click="emit('acao')"
    >
      + {{ textoBotao }}
    </button>
  </header>
</template>

<style scoped>
.cabecalho-pagina {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.categoria {
  margin: 0 0 8px;
  color: #C8102E;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 1px;
}

h1 {
  margin: 0 0 8px;
  color: #0A1F44;
  font-size: 28px;
  line-height: 1.2;
}

.descricao {
  margin: 0;
  color: #6B7280;
  font-size: 14px;
}

.botao-principal {
  padding: 12px 18px;
  border: none;
  border-radius: 8px;
  background: #C8102E;
  color: white;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
}

.botao-principal:hover {
  background: #A90D27;
}

@media (max-width: 700px) {
  .cabecalho-pagina {
    flex-direction: column;
    align-items: flex-start;
  }

  h1 {
    font-size: 24px;
  }
}
</style>