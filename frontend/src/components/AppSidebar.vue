
<script setup>
import { ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const menuAberto = ref(false)

const itensMenu = [
  {
    nome: 'Dashboard',
    rota: 'dashboard',
    icone: '▦'
  },
  {
    nome: 'Turmas e Cursos',
    rota: 'turmas-cursos',
    icone: '▤'
  },
  {
    nome: 'Alunos',
    rota: 'alunos',
    icone: '♙'
  },
  {
    nome: 'Professores',
    rota: 'professores',
    icone: '♧'
  },
  {
    nome: 'Aulas e Horários',
    rota: 'aulas-horarios',
    icone: '▦'
  },
  {
    nome: 'Avaliações',
    rota: 'avaliacoes',
    icone: '▣'
  }
]


watch(
  () => route.fullPath,
  () => {
    menuAberto.value = false
  }
)

function sair() {
  auth.logout()
  menuAberto.value = false
  router.replace({ name: 'login' })
}
</script>

<template>
  <button
    class="botao-menu-mobile"
    type="button"
    :aria-expanded="menuAberto"
    aria-controls="menu-principal"
    aria-label="Abrir ou fechar menu"
    @click="menuAberto = !menuAberto"
  >
    ☰ Menu
  </button>

  <div
    v-if="menuAberto"
    class="fundo-mobile"
    @click="menuAberto = false"
  ></div>

  <aside
    id="menu-principal"
    class="sidebar"
    :class="{ aberta: menuAberto }"
  >
    <div class="marca">
      <div class="logo">TM</div>

      <div class="marca-texto">
        <strong>Teacher Manu</strong>
        <span>Academy</span>
      </div>

      <button
        class="fechar-mobile"
        type="button"
        aria-label="Fechar menu"
        @click="menuAberto = false"
      >
        ×
      </button>
    </div>

    <div class="divisor"></div>

    <p class="titulo-menu">MENU PRINCIPAL</p>

    <nav aria-label="Navegação principal">
      <RouterLink
        v-for="item in itensMenu"
        :key="item.rota"
        :to="{ name: item.rota }"
        class="item-menu"
        :class="{ ativo: route.name === item.rota }"
        :aria-current="route.name === item.rota ? 'page' : undefined"
      >
        <span class="icone" aria-hidden="true">
          {{ item.icone }}
        </span>

        <span>{{ item.nome }}</span>
      </RouterLink>
    </nav>

    <div class="espacador"></div>

    <div class="rodape-menu">
      <div class="usuario">
        <div class="avatar">A</div>

        <div>
          <strong>Área administrativa</strong>
          <small>Teacher Manu Academy</small>
        </div>
      </div>

      <button class="botao-sair" type="button" @click="sair">
        <span aria-hidden="true">↪</span>
        Sair do sistema
      </button>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  min-width: 260px;
  height: 100vh;
  height: 100dvh;
  position: sticky;
  top: 0;
  display: flex;
  flex-direction: column;
  background: var(--color-primary, #0A1F44);
  color: white;
  padding: 24px 16px;
  box-sizing: border-box;
  overflow-y: auto;
  z-index: 100;
}

.marca {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
}

.logo {
  display: flex;
  justify-content: center;
  align-items: center;
  width: 44px;
  height: 44px;
  flex-shrink: 0;
  background: var(--color-accent, #C8102E);
  border-radius: 10px;
  font-size: 17px;
  font-weight: 700;
}

.marca-texto {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.marca-texto strong {
  font-size: 16px;
}

.marca-texto span {
  font-size: 13px;
  color: #D6DCEB;
}

.divisor {
  height: 1px;
  background: #FFFFFF22;
  margin: 24px 0;
}

.titulo-menu {
  color: #AAB8D0;
  font-size: 11px;
  letter-spacing: 1.5px;
  font-weight: 700;
  margin: 0 12px 16px;
}

nav {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.item-menu {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 16px;
  color: #D6DCEB;
  text-decoration: none;
  border-radius: 8px;
  font-size: 14px;
  transition: background 0.2s;
}

.item-menu:hover {
  background: #FFFFFF16;
  color: white;
}

.item-menu.ativo {
  background: var(--color-accent, #C8102E);
  color: white;
  font-weight: 600;
}

.icone {
  width: 24px;
  text-align: center;
  font-size: 20px;
}

.espacador {
  flex: 1;
}

.rodape-menu {
  border-top: 1px solid #FFFFFF22;
  padding-top: 20px;
}

.usuario {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.avatar {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #FFFFFF20;
  font-weight: 700;
}

.usuario strong,
.usuario small {
  display: block;
}

.usuario strong {
  font-size: 12px;
}

.usuario small {
  margin-top: 4px;
  font-size: 11px;
  color: #AAB8D0;
}

.botao-sair {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 12px 16px;
  background: transparent;
  border: 1px solid #FFFFFF40;
  border-radius: 8px;
  color: white;
  cursor: pointer;
  text-align: left;
  font-size: 14px;
}

.botao-sair:hover {
  background: #FFFFFF16;
}

.botao-menu-mobile,
.fechar-mobile,
.fundo-mobile {
  display: none;
}

@media (max-width: 850px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    width: 260px;
    max-width: 85vw;
  }

  .sidebar.aberta {
    transform: translateX(0);
  }

  .botao-menu-mobile {
    display: block;
    position: fixed;
    top: 12px;
    left: 12px;
    z-index: 90;
    padding: 10px 14px;
    border: none;
    border-radius: 8px;
    background: var(--color-primary, #0A1F44);
    color: white;
    font-weight: 600;
    cursor: pointer;
  }

  .fechar-mobile {
    display: block;
    margin-left: auto;
    background: transparent;
    border: none;
    color: white;
    font-size: 28px;
    cursor: pointer;
  }

  .fundo-mobile {
    display: block;
    position: fixed;
    inset: 0;
    background: #00000080;
    z-index: 95;
  }
}
</style>