<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const aulas = ref([])
const turmas = ref([])
const professores = ref([])
const pesquisa = ref('')
const filtroDia = ref('Todos')
const mostrarFormulario = ref(false)
const editandoId = ref(null)
const menuAbertoId = ref(null)
const carregando = ref(false)
const salvando = ref(false)
const erro = ref('')
const erroFormulario = ref('')
const mensagem = ref('')
const diasSemana = ['Domingo', 'Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado']
const novoFormulario = () => ({ nome: '', assunto: '', materia: '', data_hora: '', turma_id: '' })
const formulario = ref(novoFormulario())

function extrairLista(resposta) {
  if (Array.isArray(resposta.data)) return resposta.data
  if (Array.isArray(resposta.data?.items)) return resposta.data.items
  if (Array.isArray(resposta.data?.data)) return resposta.data.data
  return []
}
function mensagemErro(e, padrao) {
  const dados = e?.response?.data
  if (e?.response?.status === 401) return 'Sessão expirada. Faça login novamente.'
  if (e?.response?.status === 409) return 'Não foi possível concluir: este registro pode estar em uso.'
  if (e?.response?.status === 422) {
    const detalhe = dados?.detail
    if (detalhe && typeof detalhe === 'object') return `Dados inválidos: ${JSON.stringify(detalhe)}`
  }
  return dados?.message || dados?.msg || padrao
}
async function carregarDados() {
  carregando.value = true
  erro.value = ''
  try {
    const [ra, rt, rp] = await Promise.allSettled([
      api.get('/aulas/'), api.get('/turmas/'), api.get('/professores/')
    ])
    if (ra.status !== 'fulfilled' || rt.status !== 'fulfilled') {
      throw ra.status === 'rejected' ? ra.reason : rt.reason
    }
    aulas.value = extrairLista(ra.value)
    turmas.value = extrairLista(rt.value)
    if (rp.status === 'fulfilled') professores.value = extrairLista(rp.value)
    else professores.value = []
  } catch (e) {
    erro.value = mensagemErro(e, 'Não foi possível carregar as aulas e turmas.')
  } finally {
    carregando.value = false
  }
}
const nomeTurma = id => turmas.value.find(t => String(t.id) === String(id))?.nome || 'Turma não encontrada'
const nomeProfessor = turmaId => {
  const turma = turmas.value.find(t => String(t.id) === String(turmaId))
  if (!turma?.professor_id) return 'Professor não vinculado'
  return professores.value.find(p => String(p.id) === String(turma.professor_id))?.nome || 'Professor não identificado'
}
function dataLocal(valor) {
  if (!valor) return null
  const data = new Date(valor)
  return Number.isNaN(data.getTime()) ? null : data
}
function formatarData(valor) {
  const d = dataLocal(valor)
  return d ? new Intl.DateTimeFormat('pt-BR', { dateStyle: 'short' }).format(d) : 'Data inválida'
}
function formatarHora(valor) {
  const d = dataLocal(valor)
  return d ? new Intl.DateTimeFormat('pt-BR', { hour: '2-digit', minute: '2-digit' }).format(d) : '--:--'
}
function diaDaSemana(valor) {
  const d = dataLocal(valor)
  return d ? diasSemana[d.getDay()] : 'Sem dia'
}
function paraInput(valor) {
  const d = dataLocal(valor)
  if (!d) return ''
  const n = x => String(x).padStart(2, '0')
  return `${d.getFullYear()}-${n(d.getMonth() + 1)}-${n(d.getDate())}T${n(d.getHours())}:${n(d.getMinutes())}`
}
function paraApi(valor) {
  // Mantém o horário local informado, com offset explícito para a API.
  const d = new Date(valor)
  return d.toISOString()
}
const totalAulas = computed(() => aulas.value.length)
const totalTurmas = computed(() => new Set(aulas.value.map(a => a.turma_id).filter(Boolean)).size)
const proximasAulas = computed(() => aulas.value.filter(a => { const d = dataLocal(a.data_hora); return d && d.getTime() >= Date.now() }).length)
const aulasPassadas = computed(() => aulas.value.filter(a => { const d = dataLocal(a.data_hora); return d && d.getTime() < Date.now() }).length)
const aulasFiltradas = computed(() => {
  const termo = pesquisa.value.trim().toLocaleLowerCase('pt-BR')
  return aulas.value.filter(a => {
    const texto = [a.nome, a.assunto, a.materia, nomeTurma(a.turma_id), nomeProfessor(a.turma_id)].join(' ').toLocaleLowerCase('pt-BR')
    return texto.includes(termo) && (filtroDia.value === 'Todos' || diaDaSemana(a.data_hora) === filtroDia.value)
  }).sort((a, b) => (dataLocal(a.data_hora)?.getTime() || 0) - (dataLocal(b.data_hora)?.getTime() || 0))
})
const agendaSemanal = computed(() => diasSemana.slice(1).concat('Domingo').map(dia => ({ dia, aulas: aulasFiltradas.value.filter(a => diaDaSemana(a.data_hora) === dia) })))
function abrirCadastro() {
  editandoId.value = null
  formulario.value = novoFormulario()
  erroFormulario.value = ''
  mensagem.value = ''
  mostrarFormulario.value = true
  menuAbertoId.value = null
}
function editarAula(aula) {
  editandoId.value = aula.id
  formulario.value = { nome: aula.nome || '', assunto: aula.assunto || '', materia: aula.materia || '', data_hora: paraInput(aula.data_hora), turma_id: aula.turma_id || '' }
  erroFormulario.value = ''
  mensagem.value = ''
  mostrarFormulario.value = true
  menuAbertoId.value = null
}
function fecharFormulario() {
  mostrarFormulario.value = false
  editandoId.value = null
  erroFormulario.value = ''
}
async function salvarAula() {
  erroFormulario.value = ''
  mensagem.value = ''
  const f = formulario.value
  if (!f.nome.trim() || !f.data_hora || !f.turma_id) {
    erroFormulario.value = 'Preencha nome, data e horário e turma.'
    return
  }
  if (Number.isNaN(new Date(f.data_hora).getTime())) {
    erroFormulario.value = 'Informe uma data e horário válidos.'
    return
  }
  const dados = { nome: f.nome.trim(), assunto: f.assunto.trim(), materia: f.materia.trim(), data_hora: paraApi(f.data_hora), turma_id: String(f.turma_id) }
  salvando.value = true
  try {
    if (editandoId.value !== null) await api.put(`/aulas/${encodeURIComponent(editandoId.value)}`, dados)
    else await api.post('/aulas/', dados)
    const texto = editandoId.value !== null ? 'Aula atualizada com sucesso!' : 'Aula cadastrada com sucesso!'
    fecharFormulario()
    await carregarDados()
    mensagem.value = texto
  } catch (e) {
    erroFormulario.value = mensagemErro(e, 'Não foi possível salvar a aula.')
  } finally {
    salvando.value = false
  }
}
async function excluirAula(aula) {
  menuAbertoId.value = null
  if (!window.confirm(`Deseja realmente excluir a aula "${aula.nome}"?`)) return
  erro.value = ''
  mensagem.value = ''
  try {
    await api.delete(`/aulas/${encodeURIComponent(aula.id)}`)
    if (editandoId.value === aula.id) fecharFormulario()
    await carregarDados()
    mensagem.value = 'Aula excluída com sucesso!'
  } catch (e) {
    erro.value = mensagemErro(e, 'Não foi possível excluir a aula.')
  }
}
function alternarMenu(id) { menuAbertoId.value = menuAbertoId.value === id ? null : id }
function fecharMenu() { menuAbertoId.value = null }
onMounted(carregarDados)
</script>

<template>
  <div class="pagina-aulas">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <h1>Gestão de Aulas e Horários</h1>
        <p>Organize as aulas por data, horário e turma.</p>
      </header>

      <section class="indicadores" aria-label="Resumo das aulas">
        <article class="cartao"><span>Total de aulas</span><strong>{{ totalAulas }}</strong></article>
        <article class="cartao"><span>Aulas futuras</span><strong class="valor-sucesso">{{ proximasAulas }}</strong></article>
        <article class="cartao"><span>Aulas anteriores</span><strong>{{ aulasPassadas }}</strong></article>
        <article class="cartao"><span>Turmas na agenda</span><strong>{{ totalTurmas }}</strong></article>
      </section>

      <p v-if="mensagem" class="mensagem" role="status">{{ mensagem }}</p>
      <p v-if="erro" class="erro erro-geral" role="alert">{{ erro }}</p>

      <section v-if="mostrarFormulario" class="painel formulario-painel">
        <div class="topo-painel">
          <div><h2>{{ editandoId !== null ? 'Editar aula' : 'Cadastrar nova aula' }}</h2><p>Informe os dados da aula que serão salvos no banco.</p></div>
          <button type="button" class="botao-secundario" @click="fecharFormulario">Fechar</button>
        </div>
        <form @submit.prevent="salvarAula">
          <div class="campos">
            <label>Nome da aula *<input v-model="formulario.nome" name="nome" type="text" maxlength="255" required placeholder="Ex.: Aula de conversação" /></label>
            <label>Turma *<select v-model="formulario.turma_id" name="turma_id" required><option value="" disabled>Selecione uma turma</option><option v-for="turma in turmas" :key="turma.id" :value="turma.id">{{ turma.nome }}</option></select></label>
            <label>Data e horário *<input v-model="formulario.data_hora" name="data_hora" type="datetime-local" required /></label>
            <label>Matéria<input v-model="formulario.materia" name="materia" type="text" maxlength="255" placeholder="Ex.: Inglês" /></label>
            <label class="campo-largo">Assunto<input v-model="formulario.assunto" name="assunto" type="text" maxlength="255" placeholder="Ex.: Tempos verbais" /></label>
          </div>
          <p v-if="turmas.length === 0" class="aviso">Cadastre uma turma na tela Turmas e Cursos antes de criar uma aula.</p>
          <p v-if="erroFormulario" class="erro" role="alert">{{ erroFormulario }}</p>
          <div class="acoes-formulario">
            <button type="button" class="botao-secundario" @click="fecharFormulario">Cancelar</button>
            <button type="submit" class="botao-primario" :disabled="salvando || turmas.length === 0">{{ salvando ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Cadastrar aula' }}</button>
          </div>
        </form>
      </section>

      <section class="painel">
        <div class="topo-painel">
          <div><h2>Agenda semanal</h2><p>Aulas com datas específicas, agrupadas por dia da semana.</p></div>
          <button type="button" class="botao-primario" @click="abrirCadastro">+ Nova aula</button>
        </div>
        <div class="filtros">
          <input v-model="pesquisa" type="search" placeholder="Pesquisar aula, turma, professor, matéria ou assunto..." aria-label="Pesquisar aulas" />
          <select v-model="filtroDia" aria-label="Filtrar por dia"><option value="Todos">Todos os dias</option><option v-for="dia in diasSemana" :key="dia" :value="dia">{{ dia }}</option></select>
          <button type="button" class="botao-secundario" :disabled="carregando" @click="carregarDados">{{ carregando ? 'Atualizando...' : 'Atualizar dados' }}</button>
        </div>
        <p v-if="carregando" class="aviso">Carregando aulas...</p>
        <div v-else class="agenda">
          <div v-for="grupo in agendaSemanal" :key="grupo.dia" class="grupo-dia">
            <div class="dia-titulo"><h3>{{ grupo.dia }}</h3><span>{{ grupo.aulas.length }} aula(s)</span></div>
            <p v-if="grupo.aulas.length === 0" class="sem-aulas">Nenhuma aula para os filtros selecionados.</p>
            <article v-for="aula in grupo.aulas" :key="aula.id" class="aula">
              <div class="horario"><strong>{{ formatarHora(aula.data_hora) }}</strong><small>{{ formatarData(aula.data_hora) }}</small></div>
              <div class="detalhes"><h4>{{ aula.nome }}</h4><p>{{ nomeTurma(aula.turma_id) }} · {{ aula.materia || 'Matéria não informada' }}</p><small>{{ aula.assunto || 'Assunto não informado' }} · {{ nomeProfessor(aula.turma_id) }}</small></div>
              <div class="menu-acoes" :class="{ 'menu-aberto': menuAbertoId === aula.id }">
                <button type="button" class="botao-tres-pontos" :aria-label="'Ações da aula ' + aula.nome" :aria-expanded="menuAbertoId === aula.id" @click.stop="alternarMenu(aula.id)">⋮</button>
                <div v-if="menuAbertoId === aula.id" class="opcoes-menu"><button type="button" @click="editarAula(aula)">Editar</button><button type="button" class="opcao-excluir" @click="excluirAula(aula)">Excluir</button></div>
              </div>
            </article>
          </div>
        </div>
        <div class="rodape-painel">{{ aulasFiltradas.length }} aula(s) encontrada(s)</div>
      </section>
      <p class="aviso">A API registra uma data e um horário por aula. Horário final, sala, cancelamento e recorrência semanal ainda não fazem parte do cadastro atual.</p>
    </div>
    <div v-if="menuAbertoId !== null" class="overlay-menu" @click="fecharMenu"></div>
  </div>
</template>

<style scoped>
.pagina-aulas { min-height:100vh; background:#F7F8FA; color:#1F2937; font-family:inherit; font-size:14px; }
.pagina-aulas *, .pagina-aulas *::before, .pagina-aulas *::after { box-sizing:border-box; }
.pagina-aulas button, .pagina-aulas input, .pagina-aulas select { font:inherit; }
button { cursor:pointer; }
button:disabled { opacity:.6; cursor:not-allowed; }
.faixa-superior { height:6px; background:#0A1F44; }
.conteudo { width:min(1200px,94%); margin:0 auto; padding:30px 0 36px; }
.cabecalho-pagina { margin-bottom:24px; }
.cabecalho-pagina h1 { margin:0 0 8px; color:#C8102E; font-size:26px; font-weight:700; line-height:1.25; }
.cabecalho-pagina p { margin:0; color:#0A1F44; font-size:14px; }
.indicadores { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:16px; margin-bottom:24px; }
.cartao,.painel { background:#fff; border:1px solid #E2E5EA; border-radius:12px; }
.cartao { display:flex; flex-direction:column; gap:12px; padding:22px; }
.cartao span { color:#6B7280; font-size:14px; }
.cartao strong { color:#0A1F44; font-size:30px; font-weight:700; }
.cartao .valor-sucesso { color:#2E7D32; }
.painel { margin-bottom:24px; padding:24px; overflow:visible; }
.topo-painel { display:flex; align-items:center; justify-content:space-between; gap:16px; margin-bottom:18px; }
.topo-painel h2 { margin:0; color:#1F2937; font-size:18px; font-weight:600; }
.topo-painel p { margin:6px 0 0; color:#6B7280; font-size:13px; }
.botao-primario { border:none; border-radius:8px; background:#C8102E; color:#fff; padding:11px 16px; font-size:14px; font-weight:600; white-space:nowrap; }
.botao-primario:hover:not(:disabled) { background:#A90D27; }
.botao-secundario { border:1px solid #E2E5EA; border-radius:8px; background:#fff; color:#0A1F44; padding:10px 15px; font-size:14px; }
.campos { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:16px; }
.campos label { display:flex; flex-direction:column; gap:7px; color:#6B7280; font-size:13px; }
.campo-largo { grid-column:1 / -1; }
input,select { width:100%; min-width:0; border:1px solid #E2E5EA; border-radius:8px; background:#fff; color:#1F2937; padding:11px 12px; font-size:14px; }
input::placeholder { color:#6B7280; }
input:focus,select:focus { outline:2px solid #0A1F44; outline-offset:1px; }
.acoes-formulario { display:flex; justify-content:flex-end; flex-wrap:wrap; gap:12px; margin-top:24px; }
.erro { color:#DC2626; font-size:13px; margin-top:16px; }
.erro-geral { margin-bottom:20px; }
.mensagem { background:#E8F5E9; color:#2E7D32; border-radius:8px; padding:14px; margin-bottom:20px; }
.filtros { display:grid; grid-template-columns:minmax(0,1fr) 180px auto; gap:12px; margin-bottom:20px; }
.grupo-dia { margin-top:22px; }
.dia-titulo { display:flex; align-items:center; justify-content:space-between; gap:12px; padding-bottom:10px; border-bottom:1px solid #E2E5EA; }
.dia-titulo h3 { margin:0; color:#0A1F44; font-size:15px; font-weight:600; }
.dia-titulo span { color:#6B7280; font-size:12px; }
.sem-aulas { margin:0; padding:16px 0; color:#6B7280; font-size:13px; }
.aula { display:flex; align-items:center; gap:18px; padding:18px 0; border-bottom:1px solid #E2E5EA; }
.horario { display:flex; flex-direction:column; min-width:90px; gap:5px; }
.horario strong { color:#0A1F44; font-size:14px; font-weight:600; }
.horario small,.detalhes small { color:#6B7280; font-size:12px; }
.detalhes { flex:1; min-width:0; }
.detalhes h4 { margin:0 0 6px; color:#0A1F44; font-size:13px; font-weight:600; }
.detalhes p { margin:0 0 6px; color:#1F2937; font-size:13px; }
.menu-acoes { position:relative; display:inline-block; z-index:1; }
.menu-acoes.menu-aberto { z-index:101; }
.botao-tres-pontos { border:none; background:transparent; color:#0A1F44; font-size:20px; padding:5px 10px; border-radius:6px; line-height:1; }
.botao-tres-pontos:hover { background:#F1F3F6; }
.opcoes-menu { position:absolute; top:100%; right:0; z-index:102; min-width:155px; background:#fff; border:1px solid #E2E5EA; border-radius:8px; box-shadow:0 6px 20px #00000020; padding:5px; }
.opcoes-menu button { display:block; width:100%; border:none; border-radius:5px; background:transparent; color:#0A1F44; text-align:left; font-size:13px; padding:10px; }
.opcoes-menu button:hover { background:#F1F3F6; }
.opcoes-menu .opcao-excluir { color:#DC2626; }
.overlay-menu { position:fixed; inset:0; z-index:50; background:transparent; }
.rodape-painel { padding-top:18px; color:#6B7280; font-size:12px; }
.aviso { color:#6B7280; font-size:12px; line-height:1.6; }
@media (max-width:1100px) { .indicadores { grid-template-columns:repeat(2,minmax(0,1fr)); } .aula { flex-wrap:wrap; } }
@media (max-width:700px) { .conteudo { padding:24px 0; } .indicadores,.campos,.filtros { grid-template-columns:1fr; } .campo-largo { grid-column:auto; } .topo-painel { align-items:flex-start; flex-direction:column; } .painel { padding:16px; } .cabecalho-pagina h1 { font-size:23px; } .aula { gap:12px; } }
</style>
