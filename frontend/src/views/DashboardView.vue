<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useRouter } from 'vue-router'
import api from '@/services/api'

const auth = useAuthStore()
const router = useRouter()
const alunos = ref([])
const professores = ref([])
const turmas = ref([])
const cursos = ref([])
const aulas = ref([])
const avaliacoes = ref([])
const carregando = ref(false)
const erro = ref('')
const avisos = ref([])
const NOTA_MINIMA = 7

function lista(resposta) {
  const dados = resposta?.data
  if (Array.isArray(dados)) return dados
  for (const chave of ['items', 'results', 'data', 'alunos', 'professores', 'turmas', 'cursos', 'aulas', 'avaliacoes']) {
    if (Array.isArray(dados?.[chave])) return dados[chave]
  }
  throw new Error('Formato de listagem inesperado')
}
async function carregar() {
  carregando.value = true
  erro.value = ''
  avisos.value = []
  const fontes = [
    ['/alunos/', alunos, 'alunos'],
    ['/professores/', professores, 'professores'],
    ['/turmas/', turmas, 'turmas'],
    ['/cursos/', cursos, 'cursos'],
    ['/aulas/', aulas, 'aulas'],
    ['/avaliacoes/', avaliacoes, 'avaliações']
  ]
  const resultados = await Promise.allSettled(fontes.map(async ([url, destino]) => {
    const resposta = await api.get(url)
    return lista(resposta)
  }))
  resultados.forEach((resultado, indice) => {
    const [, destino, nome] = fontes[indice]
    if (resultado.status === 'fulfilled') destino.value = resultado.value
    else {
      destino.value = []
      avisos.value.push(nome)
    }
  })
  if (avisos.value.length) erro.value = `Não foi possível carregar: ${avisos.value.join(', ')}. Os indicadores correspondentes estão indisponíveis.`
  carregando.value = false
}
const contagem = (dados, nome) => avisos.value.includes(nome) ? '—' : dados.length
const indicadores = computed(() => [
  { titulo: 'Alunos cadastrados', valor: contagem(alunos.value, 'alunos'), descricao: 'Registros de alunos', icone: '🎓' },
  { titulo: 'Professores cadastrados', valor: contagem(professores.value, 'professores'), descricao: 'Equipe pedagógica', icone: '👩‍🏫' },
  { titulo: 'Turmas cadastradas', valor: contagem(turmas.value, 'turmas'), descricao: `${avisos.value.includes('cursos') ? '—' : cursos.value.length} curso(s) cadastrado(s)`, icone: '📚' },
  { titulo: 'Aulas cadastradas', valor: contagem(aulas.value, 'aulas'), descricao: 'Aulas registradas no sistema', icone: '📅' }
])
const modulos = [
  { titulo: 'Turmas e Cursos', descricao: 'Organize cursos, turmas e matrículas.', icone: '📚', rota: '/turmas-cursos' },
  { titulo: 'Alunos', descricao: 'Consulte e gerencie os alunos.', icone: '🎓', rota: '/alunos' },
  { titulo: 'Professores', descricao: 'Gerencie a equipe de professores.', icone: '👩‍🏫', rota: '/professores' },
  { titulo: 'Avaliações e Desempenho', descricao: 'Acompanhe notas e resultados.', icone: '📊', rota: '/avaliacoes' },
  { titulo: 'Aulas e Horários', descricao: 'Organize a agenda de aulas.', icone: '📅', rota: '/aulas-horarios' }
]
const turmasPorId = computed(() => new Map(turmas.value.map(t => [String(t.id), t])))
const alunosPorId = computed(() => new Map(alunos.value.map(a => [String(a.id), a])))
const aulasPorId = computed(() => new Map(aulas.value.map(a => [String(a.id), a])))
const professoresPorId = computed(() => new Map(professores.value.map(p => [String(p.id), p])))
function nomeTurma(id) { const t = turmasPorId.value.get(String(id)); return t?.nome || t?.titulo || 'Turma não encontrada' }
function nomeProfessor(turmaId) {
  const turma = turmasPorId.value.get(String(turmaId))
  if (!turma) return 'Professor não informado'
  return turma.professor?.nome || professoresPorId.value.get(String(turma.professor_id))?.nome || 'Professor não informado'
}
function dataValida(valor) { const d = valor ? new Date(valor) : new Date(NaN); return Number.isNaN(d.getTime()) ? null : d }
function formatarData(valor) { const d = dataValida(valor); return d ? d.toLocaleDateString('pt-BR') : 'Data não informada' }
function formatarHora(valor) { const d = dataValida(valor); return d ? d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '—' }
const proximasAulas = computed(() => aulas.value.filter(a => {
  const d = dataValida(a.data_hora)
  return d && d >= new Date()
}).sort((a,b) => new Date(a.data_hora) - new Date(b.data_hora)).slice(0, 5).map(a => ({
  ...a, turma: nomeTurma(a.turma_id), professor: nomeProfessor(a.turma_id)
})))
const notasValidas = computed(() => avaliacoes.value.map(a => a.nota).filter(n => n !== null && n !== undefined && n !== '' && Number.isFinite(Number(n))).map(Number))
const mediaGeral = computed(() => notasValidas.value.length ? notasValidas.value.reduce((s,n) => s+n,0) / notasValidas.value.length : null)
const satisfatorias = computed(() => notasValidas.value.filter(n => n >= NOTA_MINIMA).length)
const abaixoMedia = computed(() => notasValidas.value.filter(n => n < NOTA_MINIMA).length)
function formatarNota(n) { return n === null ? '—' : n.toFixed(1).replace('.', ',') }
const atividades = computed(() => {
  const registros = []
  for (const a of aulas.value) {
    if (dataValida(a.data_hora)) registros.push({ id: `a-${a.id}`, data: a.data_hora, titulo: 'Aula cadastrada', descricao: `${a.nome || 'Aula'} · ${nomeTurma(a.turma_id)}`, icone: '📅' })
  }
  // A data da aula não é a data de cadastro; a lista abaixo é apenas um resumo de registros com data.
  return registros.sort((a,b) => new Date(b.data) - new Date(a.data)).slice(0, 4)
})
function navegar(rota) { router.push(rota) }
function sair() { auth.logout(); router.push({ name: 'login' }) }
onMounted(carregar)
</script>

<template>
  <div class="pagina-dashboard">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <div><h1>Dashboard</h1><p>Bem-vindo ao Teacher Manu Academy. Acompanhe as principais informações da escola.</p></div>
        <button type="button" class="botao-sair" @click="sair">Sair</button>
      </header>
      <p v-if="erro" class="aviso" role="alert">{{ erro }}</p>
      <p v-if="carregando" class="aviso" role="status">Carregando informações...</p>
      <section class="indicadores" aria-label="Resumo geral da escola">
        <article v-for="indicador in indicadores" :key="indicador.titulo" class="cartao-indicador">
          <div class="indicador-topo"><span class="indicador-titulo">{{ indicador.titulo }}</span><span class="indicador-icone" aria-hidden="true">{{ indicador.icone }}</span></div>
          <strong class="indicador-valor">{{ carregando ? '…' : indicador.valor }}</strong>
          <small class="indicador-descricao">{{ indicador.descricao }}</small>
        </article>
      </section>
      <section class="painel">
        <div class="topo-painel"><div><h2>Acesso rápido</h2><p>Acesse as principais áreas de gestão da escola.</p></div></div>
        <div class="grade-modulos">
          <button v-for="modulo in modulos" :key="modulo.titulo" type="button" class="cartao-modulo" @click="navegar(modulo.rota)">
            <span class="modulo-icone" aria-hidden="true">{{ modulo.icone }}</span>
            <strong>{{ modulo.titulo }}</strong><span class="modulo-descricao">{{ modulo.descricao }}</span><span class="modulo-link">Acessar módulo →</span>
          </button>
        </div>
      </section>
      <div class="grade-inferior">
        <section class="painel">
          <div class="topo-painel"><div><h2>Próximas aulas</h2><p>Aulas futuras cadastradas no sistema.</p></div></div>
          <div class="lista-aulas">
            <p v-if="!proximasAulas.length" class="aviso">{{ avisos.includes('aulas') ? 'Agenda indisponível.' : 'Nenhuma aula futura cadastrada.' }}</p>
            <article v-for="aula in proximasAulas" :key="aula.id" class="item-aula">
              <div class="aula-topo"><div><strong>{{ aula.turma }}</strong><span class="aula-dia">{{ formatarData(aula.data_hora) }}</span></div><span class="status agendada">Programada</span></div>
              <p>{{ aula.nome }}<span v-if="aula.materia"> · {{ aula.materia }}</span></p>
              <div class="aula-detalhes"><span>🕒 {{ formatarHora(aula.data_hora) }}</span><span>👩‍🏫 {{ aula.professor }}</span></div>
            </article>
          </div>
          <button type="button" class="link-painel" @click="navegar('/aulas-horarios')">Ver agenda completa →</button>
        </section>
        <section class="painel">
          <div class="topo-painel"><div><h2>Registros acadêmicos</h2><p>Aulas registradas, organizadas pela data da aula (não pela data do cadastro).</p></div></div>
          <div class="lista-atividades">
            <p v-if="!atividades.length" class="aviso">Nenhum registro de aula com data disponível.</p>
            <article v-for="atividade in atividades" :key="atividade.id" class="item-atividade">
              <div class="atividade-icone" aria-hidden="true">{{ atividade.icone }}</div>
              <div class="atividade-texto"><strong>{{ atividade.titulo }}</strong><p>{{ atividade.descricao }} · {{ formatarData(atividade.data) }}</p></div>
            </article>
          </div>
          <div class="resumo-painel">
            <h3>Resumo acadêmico</h3>
            <div class="linha-resumo"><span>Avaliações cadastradas</span><strong>{{ avisos.includes('avaliações') ? '—' : avaliacoes.length }}</strong></div>
            <div class="linha-resumo"><span>Média geral das avaliações</span><strong>{{ avisos.includes('avaliações') ? '—' : formatarNota(mediaGeral) }}</strong></div>
            <div class="linha-resumo"><span>Notas satisfatórias</span><strong class="texto-verde">{{ avisos.includes('avaliações') ? '—' : satisfatorias }}</strong></div>
            <div class="linha-resumo"><span>Notas abaixo de 7</span><strong class="texto-vermelho">{{ avisos.includes('avaliações') ? '—' : abaixoMedia }}</strong></div>
            <button type="button" class="link-painel" @click="navegar('/avaliacoes')">Ver avaliações →</button>
          </div>
        </section>
      </div>
      <p class="aviso">Dados consultados na API. Atualize a página para recarregar os indicadores. Aulas futuras são identificadas pela data e hora cadastradas.</p>
      <button type="button" class="botao-sair" @click="carregar" :disabled="carregando">Atualizar indicadores</button>
    </div>
  </div>
</template>

<style scoped>
.pagina-dashboard {
  min-height: 100vh;
  background: #F7F8FA;
  color: #1F2937;
  font-family: inherit;
  font-size: 14px;
}

.pagina-dashboard *,
.pagina-dashboard *::before,
.pagina-dashboard *::after {
  box-sizing: border-box;
}

.pagina-dashboard button {
  font: inherit;
  cursor: pointer;
}

/* Faixa azul superior */
.faixa-superior {
  height: 6px;
  background: #0A1F44;
}

/* Conteúdo */
.conteudo {
  width: min(1200px, 94%);
  margin: 0 auto;
  padding: 30px 0 36px;
}

/* Cabeçalho */
.cabecalho-pagina {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.cabecalho-pagina h1 {
  margin: 0 0 8px;
  color: #C8102E;
  font-size: 26px;
  font-weight: 700;
  line-height: 1.25;
}

.cabecalho-pagina p {
  margin: 0;
  color: #0A1F44;
  font-size: 14px;
  line-height: 1.6;
}

.botao-sair {
  border: 1px solid #E2E5EA;
  border-radius: 8px;
  background: #FFFFFF;
  color: #C8102E;
  padding: 10px 16px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.botao-sair:hover {
  background: #FFF1F2;
  border-color: #C8102E;
}

/* Indicadores */
.indicadores {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.cartao-indicador,
.painel {
  background: #FFFFFF;
  border: 1px solid #E2E5EA;
  border-radius: 12px;
}

.cartao-indicador {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 22px;
}

.indicador-topo {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
}

.indicador-titulo {
  color: #6B7280;
  font-size: 13px;
  line-height: 1.5;
}

.indicador-icone {
  display: grid;
  place-items: center;
  width: 34px;
  height: 34px;
  flex-shrink: 0;
  border-radius: 9px;
  background: #F1F3F6;
  font-size: 18px;
}

.indicador-valor {
  color: #0A1F44;
  font-size: 30px;
  font-weight: 700;
  line-height: 1;
}

.indicador-descricao {
  color: #6B7280;
  font-size: 12px;
}

/* Painéis */
.painel {
  padding: 24px;
  margin-bottom: 24px;
}

.topo-painel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 20px;
}

.topo-painel h2 {
  margin: 0;
  color: #1F2937;
  font-size: 18px;
  font-weight: 600;
}

.topo-painel p {
  margin: 6px 0 0;
  color: #6B7280;
  font-size: 13px;
  line-height: 1.5;
}

/* Acesso rápido */
.grade-modulos {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.cartao-modulo {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  min-height: 170px;
  padding: 18px;
  text-align: left;
  border: 1px solid #E2E5EA;
  border-radius: 10px;
  background: #FFFFFF;
  color: #1F2937;
  transition:
    border-color 0.2s ease,
    background 0.2s ease,
    transform 0.2s ease;
}

.cartao-modulo:hover {
  border-color: #0A1F44;
  background: #FAFBFD;
  transform: translateY(-2px);
}

.modulo-icone {
  display: grid;
  place-items: center;
  width: 38px;
  height: 38px;
  border-radius: 9px;
  background: #F1F3F6;
  font-size: 20px;
}

.cartao-modulo strong {
  color: #0A1F44;
  font-size: 14px;
  font-weight: 600;
}

.modulo-descricao {
  color: #6B7280;
  font-size: 12px;
  line-height: 1.5;
}

.modulo-link {
  margin-top: auto;
  color: #C8102E;
  font-size: 12px;
  font-weight: 600;
}

/* Parte inferior */
.grade-inferior {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 24px;
}

.grade-inferior .painel {
  min-width: 0;
}

/* Agenda */
.item-aula {
  padding: 16px 0;
  border-bottom: 1px solid #E2E5EA;
}

.item-aula:first-child {
  padding-top: 0;
}

.aula-topo {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.aula-topo strong {
  display: block;
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.aula-dia {
  display: block;
  margin-top: 5px;
  color: #6B7280;
  font-size: 12px;
}

.item-aula p {
  margin: 10px 0;
  color: #1F2937;
  font-size: 13px;
}

.aula-detalhes {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #6B7280;
  font-size: 12px;
}

.status {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
}

.status.agendada {
  background: #DDF5E7;
  color: #008C45;
}

/* Atividades */
.item-atividade {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px 0;
  border-bottom: 1px solid #E2E5EA;
}

.item-atividade:first-child {
  padding-top: 0;
}

.atividade-icone {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  border-radius: 9px;
  background: #F1F3F6;
  font-size: 17px;
}

.atividade-texto strong {
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.atividade-texto p {
  margin: 6px 0 0;
  color: #6B7280;
  font-size: 12px;
  line-height: 1.5;
}

/* Resumo acadêmico */
.resumo-painel {
  padding-top: 22px;
}

.resumo-painel h3 {
  margin: 0 0 16px;
  color: #0A1F44;
  font-size: 15px;
  font-weight: 600;
}

.linha-resumo {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 10px 0;
  border-bottom: 1px solid #E2E5EA;
}

.linha-resumo span {
  color: #6B7280;
  font-size: 12px;
}

.linha-resumo strong {
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.linha-resumo .texto-verde {
  color: #2E7D32;
}

.linha-resumo .texto-vermelho {
  color: #DC2626;
}

/* Links */
.link-painel {
  display: inline-block;
  margin-top: 18px;
  padding: 0;
  border: none;
  background: transparent;
  color: #C8102E;
  font-size: 13px;
  font-weight: 600;
  text-align: left;
}

.link-painel:hover {
  text-decoration: underline;
}

/* Aviso */
.aviso {
  color: #6B7280;
  font-size: 12px;
  line-height: 1.6;
}

/* Fonte original do sistema */
.pagina-dashboard,
.pagina-dashboard h1,
.pagina-dashboard h2,
.pagina-dashboard h3,
.pagina-dashboard h4,
.pagina-dashboard p,
.pagina-dashboard span,
.pagina-dashboard strong,
.pagina-dashboard small,
.pagina-dashboard button {
  font-family: inherit;
}

/* Responsividade */
@media (max-width: 1100px) {
  .indicadores {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .grade-modulos {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 800px) {
  .grade-inferior {
    grid-template-columns: 1fr;
    gap: 0;
  }
}

@media (max-width: 600px) {
  .conteudo {
    padding: 24px 0;
  }

  .cabecalho-pagina {
    flex-direction: column;
    align-items: flex-start;
  }

  .indicadores,
  .grade-modulos {
    grid-template-columns: 1fr;
  }

  .painel {
    padding: 16px;
  }

  .cabecalho-pagina h1 {
    font-size: 23px;
  }

  .cartao-modulo {
    min-height: 150px;
  }
}
</style>
