<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const email = ref('')
const senha = ref('')
const erro = ref('')
const carregando = ref(false)

const auth = useAuthStore()
const router = useRouter()

async function entrar() {
  erro.value = ''
  carregando.value = true
  try {
    await auth.login(email.value, senha.value)
    router.push({ name: 'dashboard' })
  } catch (e) {
    if (e.response && (e.response.status === 401 || e.response.status === 422)) {
      erro.value = e.response.data.message || 'Preencha email e senha corretamente'
    } else {
      erro.value = 'Não foi possível conectar ao servidor'
    }
  } finally {
    carregando.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <section class="apresentacao">
      <h1>Teacher Manu Academy</h1>
      <p class="subtitulo">Sistema de Gestão Educacional</p>
      <p class="descricao">
        Centralize informações de professores, alunos, cursos e turmas.
        Acompanhe o desempenho de cada aluno e tenha uma visão completa
        para apoiar as decisões da escola.
      </p>
      <ul class="destaques">
        <li>Gestão de professores e turmas</li>
        <li>Acompanhamento individual de alunos</li>
        <li>Avaliações e histórico centralizados</li>
      </ul>
    </section>

    <section class="login-box">
      <form class="login-form" @submit.prevent="entrar">
        <h2>Entrar</h2>

        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" required autocomplete="username" />

        <label for="senha">Senha</label>
        <input id="senha" v-model="senha" type="password" required autocomplete="current-password" />

        <p v-if="erro" class="erro">{{ erro }}</p>

        <button type="submit" :disabled="carregando">
          {{ carregando ? 'Entrando...' : 'Entrar' }}
        </button>
      </form>
    </section>
  </div>
</template>

<style scoped>
.login-page {
  display: flex;
  min-height: 100vh;
  min-height: 100dvh;
}

.apresentacao {
  flex: 1;
  background-color: var(--color-primary);
  color: white;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 4rem;
  padding-top: calc(4rem + env(safe-area-inset-top, 0px));
}

.apresentacao h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
.subtitulo { font-size: 1.1rem; color: var(--color-accent); font-weight: 600; margin-bottom: 1.5rem; }
.descricao { max-width: 32rem; line-height: 1.6; color: #D6DCEB; margin-bottom: 2rem; }
.destaques { list-style: none; display: flex; flex-direction: column; gap: 0.75rem; }
.destaques li { padding-left: 1.5rem; position: relative; color: #D6DCEB; }
.destaques li::before { content: "✓"; position: absolute; left: 0; color: var(--color-accent); font-weight: bold; }

.login-box {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: var(--color-surface);
  padding: 2rem;
  padding-bottom: calc(2rem + env(safe-area-inset-bottom, 0px));
}

.login-form { width: 100%; max-width: 22rem; display: flex; flex-direction: column; gap: 0.5rem; }
.login-form h2 { margin-bottom: 1rem; color: var(--color-primary); }
.login-form label { font-size: 0.875rem; color: var(--color-text-secondary); margin-top: 0.75rem; }

.login-form input {
  padding: 0.75rem;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  font-size: 16px;
  min-height: 44px;
}
.login-form input:focus { outline: none; border-color: var(--color-primary); }

.login-form button {
  margin-top: 1.5rem;
  padding: 0.85rem;
  background-color: var(--color-accent);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  min-height: 48px;
}
.login-form button:disabled { opacity: 0.6; cursor: not-allowed; }

.erro { color: var(--color-error); font-size: 0.875rem; margin-top: 0.5rem; }

@media (max-width: 900px) {
  .apresentacao,
  .login-box {
    padding: 2.5rem;
  }
}

@media (max-width: 640px) {
  .login-page {
    flex-direction: column;
  }

  .apresentacao {
    flex: none;
    padding: 1.5rem 1.5rem 1.25rem;
    padding-top: calc(1.5rem + env(safe-area-inset-top, 0px));
    text-align: center;
    align-items: center;
  }

  .apresentacao h1 { font-size: 1.5rem; }
  .subtitulo { font-size: 0.95rem; margin-bottom: 0; }

  .descricao,
  .destaques {
    display: none;
  }

  .login-box {
    flex: 1;
    padding: 1.5rem;
    align-items: flex-start;
    padding-top: 2rem;
  }
}
</style>
