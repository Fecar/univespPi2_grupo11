<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const NOTA_MINIMA = 7
const avaliacoes = ref([])
const alunos = ref([])
const aulas = ref([])
const turmas = ref([])
const pesquisa = ref('')
const filtroStatus = ref('Todos')
const mostrarFormulario = ref(false)
const editandoId = ref(null)
const menuAbertoId = ref(null)
const carregando = ref(false)
const salvando = ref(false)
const erro = ref('')
const mensagem = ref('')
const formularioVazio = () => ({ aluno_id: '', aula_id: '', nota: '' })
const formulario = ref(formularioVazio())

function extrairLista(resposta) {
  const dados = resposta.data
  if (Array.isArray(dados)) return dados
  if (Array.isArray(dados?.items)) return dados.items
  if (Array.isArray(dados?.data)) return dados.data
  return []
}
function mensagemErro(e, padrao) {
  const dados = e?.response?.data
  if (typeof dados?.message === 'string') return dados.message
  if (typeof dados?.msg === 'string') return dados.msg
  if (dados?.detail && typeof dados.detail === 'object') {
    const detalhes = Object.entries(dados.detail).map(([campo, valor]) => `${campo}: ${Array.isArray(valor) ? valor.join(', ') : JSON.stringify(valor)}`)
    if (detalhes.length) return detalhes.join(' | ')
  }
  return padrao
}
async function carregarDados() {
  carregando.value = true
  erro.value = ''
  try {
    const [rAvaliacoes, rAlunos, rAulas, rTurmas] = await Promise.all([
      api.get('/avaliacoes/'), api.get('/alunos/'), api.get('/aulas/'), api.get('/turmas/')
    ])
    avaliacoes.value = extrairLista(rAvaliacoes)
    alunos.value = extrairLista(rAlunos)
    aulas.value = extrairLista(rAulas)
    turmas.value = extrairLista(rTurmas)
  } catch (e) {
    erro.value = mensagemErro(e, 'Não foi possível carregar as avaliações e seus vínculos.')
  } finally {
    carregando.value = false
  }
}
onMounted(carregarDados)
const alunoPorId = id => alunos.value.find(a => String(a.id) === String(id))
const aulaPorId = id => aulas.value.find(a => String(a.id) === String(id))
const turmaPorId = id => turmas.value.find(t => String(t.id) === String(id))
const nomeAluno = id => alunoPorId(id)?.nome || 'Aluno não encontrado'
const nomeAula = id => aulaPorId(id)?.nome || 'Aula não encontrada'
const nomeTurma = id => turmaPorId(aulaPorId(id)?.turma_id)?.nome || '—'
const dataAula = id => aulaPorId(id)?.data_hora || null
const temNota = item => item.nota !== null && item.nota !== undefined && item.nota !== ''
const notas = computed(() => avaliacoes.value.filter(temNota))
const totalAvaliacoes = computed(() => avaliacoes.value.length)
const mediaGeral = computed(() => notas.value.length ? notas.value.reduce((s, a) => s + Number(a.nota), 0) / notas.value.length : null)
const satisfatorias = computed(() => notas.value.filter(a => Number(a.nota) >= NOTA_MINIMA).length)
const abaixoMedia = computed(() => notas.value.filter(a => Number(a.nota) < NOTA_MINIMA).length)
const avaliacoesFiltradas = computed(() => {
  const termo = pesquisa.value.trim().toLocaleLowerCase('pt-BR')
  return avaliacoes.value.filter(item => {
    const texto = [nomeAluno(item.aluno_id), nomeAula(item.aula_id), nomeTurma(item.aula_id), aulaPorId(item.aula_id)?.materia, aulaPorId(item.aula_id)?.assunto].join(' ').toLocaleLowerCase('pt-BR')
    const status = !temNota(item) ? 'Pendente' : Number(item.nota) >= NOTA_MINIMA ? 'Satisfatorio' : 'Abaixo'
    return texto.includes(termo) && (filtroStatus.value === 'Todos' || filtroStatus.value === status)
  })
})
function formatarNota(nota) { return nota === null || nota === undefined || nota === '' ? '—' : Number(nota).toFixed(1).replace('.', ',') }
function formatarData(valor) {
  if (!valor) return '—'
  const data = new Date(valor)
  return Number.isNaN(data.getTime()) ? '—' : data.toLocaleDateString('pt-BR')
}
function abrirCadastro() {
  formulario.value = formularioVazio()
  editandoId.value = null
  mostrarFormulario.value = true
  menuAbertoId.value = null
  erro.value = ''
  mensagem.value = ''
}
function editarAvaliacao(item) {
  formulario.value = { aluno_id: String(item.aluno_id), aula_id: String(item.aula_id), nota: temNota(item) ? String(item.nota) : '' }
  editandoId.value = item.id
  mostrarFormulario.value = true
  menuAbertoId.value = null
  erro.value = ''
  mensagem.value = ''
}
function cancelar() { mostrarFormulario.value = false; editandoId.value = null; erro.value = '' }
async function salvarAvaliacao() {
  if (salvando.value) return
  erro.value = ''
  mensagem.value = ''
  if (!formulario.value.aluno_id || !formulario.value.aula_id) {
    erro.value = 'Selecione o aluno e a aula.'
    return
  }
  const texto = String(formulario.value.nota).trim().replace(',', '.')
  const nota = texto === '' ? null : Number(texto)
  if (nota !== null && (!Number.isFinite(nota) || nota < 0 || nota > 10)) {
    erro.value = 'A nota deve estar entre 0 e 10.'
    return
  }
  const dados = { aluno_id: formulario.value.aluno_id, aula_id: formulario.value.aula_id, nota }
  salvando.value = true
  try {
    if (editandoId.value !== null) await api.put(`/avaliacoes/${editandoId.value}`, dados)
    else await api.post('/avaliacoes/', dados)
    const textoSucesso = editandoId.value !== null ? 'Avaliação atualizada com sucesso!' : 'Avaliação cadastrada com sucesso!'
    cancelar()
    await carregarDados()
    mensagem.value = textoSucesso
  } catch (e) {
    erro.value = mensagemErro(e, 'Não foi possível salvar a avaliação.')
  } finally { salvando.value = false }
}
async function excluirAvaliacao(item) {
  menuAbertoId.value = null
  if (!window.confirm(`Deseja realmente excluir a avaliação de ${nomeAluno(item.aluno_id)}?`)) return
  erro.value = ''
  mensagem.value = ''
  try {
    await api.delete(`/avaliacoes/${item.id}`)
    await carregarDados()
    mensagem.value = 'Avaliação excluída com sucesso!'
  } catch (e) { erro.value = mensagemErro(e, 'Não foi possível excluir a avaliação.') }
}
function alternarMenu(id) { menuAbertoId.value = menuAbertoId.value === id ? null : id }
function fecharMenu() { menuAbertoId.value = null }
</script>

<template>
  <div class="pagina-avaliacoes">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <h1>Avaliações e Desempenho</h1>
        <p>Registre avaliações e acompanhe o desempenho dos alunos.</p>
      </header>
      <section class="indicadores" aria-label="Resumo das avaliações">
        <article class="cartao"><span>Total de avaliações</span><strong>{{ totalAvaliacoes }}</strong></article>
        <article class="cartao"><span>Média geral</span><strong>{{ formatarNota(mediaGeral) }}</strong></article>
        <article class="cartao"><span>Notas satisfatórias</span><strong class="valor-sucesso">{{ satisfatorias }}</strong></article>
        <article class="cartao"><span>Notas abaixo de 7</span><strong class="valor-alerta">{{ abaixoMedia }}</strong></article>
      </section>
      <p v-if="mensagem" class="mensagem" role="status">{{ mensagem }}</p>
      <p v-if="erro && !mostrarFormulario" class="erro" role="alert">{{ erro }}</p>
      <section v-if="mostrarFormulario" class="painel formulario-painel">
        <div class="topo-painel">
          <div><h2>{{ editandoId !== null ? 'Editar avaliação' : 'Cadastrar nova avaliação' }}</h2><p>Vincule a avaliação a um aluno e uma aula existentes.</p></div>
          <button type="button" class="botao-secundario" @click="cancelar">Fechar</button>
        </div>
        <form @submit.prevent="salvarAvaliacao">
          <div class="campos">
            <label>Aluno *
              <select v-model="formulario.aluno_id" name="aluno_id" required>
                <option value="" disabled>Selecione um aluno</option>
                <option v-for="aluno in alunos" :key="aluno.id" :value="String(aluno.id)">{{ aluno.nome }}</option>
              </select>
            </label>
            <label>Aula *
              <select v-model="formulario.aula_id" name="aula_id" required>
                <option value="" disabled>Selecione uma aula</option>
                <option v-for="aula in aulas" :key="aula.id" :value="String(aula.id)">{{ aula.nome }} · {{ nomeTurma(aula.id) }} · {{ formatarData(aula.data_hora) }}</option>
              </select>
            </label>
            <label>Nota (0 a 10) — opcional
              <input v-model="formulario.nota" name="nota" type="number" min="0" max="10" step="0.1" placeholder="Sem nota por enquanto" />
            </label>
          </div>
          <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
          <p v-if="!alunos.length || !aulas.length" class="erro">Cadastre pelo menos um aluno e uma aula antes de criar avaliações.</p>
          <div class="acoes-formulario">
            <button type="button" class="botao-secundario" @click="cancelar">Cancelar</button>
            <button type="submit" class="botao-primario" :disabled="salvando || !alunos.length || !aulas.length">{{ salvando ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Cadastrar avaliação' }}</button>
          </div>
        </form>
      </section>
      <section class="painel">
        <div class="topo-painel">
          <div><h2>Avaliações cadastradas</h2><p>Consulte notas e avaliações registradas no banco de dados.</p></div>
          <button type="button" class="botao-primario" @click="abrirCadastro">+ Nova avaliação</button>
        </div>
        <div class="filtros">
          <input v-model="pesquisa" name="pesquisa" type="search" placeholder="Pesquisar aluno, turma ou aula..." aria-label="Pesquisar avaliações" />
          <select v-model="filtroStatus" name="filtroStatus" aria-label="Filtrar desempenho">
            <option value="Todos">Todos os desempenhos</option>
            <option value="Satisfatorio">Nota igual ou acima de 7</option>
            <option value="Abaixo">Nota abaixo de 7</option>
            <option value="Pendente">Sem nota</option>
          </select>
        </div>
        <div class="tabela-container">
          <table class="tabela-avaliacoes">
            <thead><tr><th>Aluno</th><th>Turma</th><th>Aula</th><th>Data da aula</th><th>Nota</th><th>Desempenho</th><th class="coluna-acoes">Ações</th></tr></thead>
            <tbody>
              <tr v-for="item in avaliacoesFiltradas" :key="item.id">
                <td><strong class="nome-aluno">{{ nomeAluno(item.aluno_id) }}</strong></td>
                <td>{{ nomeTurma(item.aula_id) }}</td>
                <td>{{ nomeAula(item.aula_id) }}</td>
                <td>{{ formatarData(dataAula(item.aula_id)) }}</td>
                <td><strong :class="temNota(item) ? Number(item.nota) >= NOTA_MINIMA ? 'nota-boa' : 'nota-baixa' : ''">{{ formatarNota(item.nota) }}</strong></td>
                <td><span class="status" :class="!temNota(item) ? '' : Number(item.nota) >= NOTA_MINIMA ? 'satisfatorio' : 'abaixo'">{{ !temNota(item) ? 'Sem nota' : Number(item.nota) >= NOTA_MINIMA ? 'Satisfatório' : 'Abaixo da média' }}</span></td>
                <td class="coluna-acoes">
                  <div class="menu-acoes" :class="{ 'menu-aberto': menuAbertoId === item.id }">
                    <button type="button" class="botao-tres-pontos" :aria-label="'Ações da avaliação de ' + nomeAluno(item.aluno_id)" :aria-expanded="menuAbertoId === item.id" aria-haspopup="true" @click.stop="alternarMenu(item.id)">⋮</button>
                    <div v-if="menuAbertoId === item.id" class="opcoes-menu">
                      <button type="button" @click="editarAvaliacao(item)">Editar</button>
                      <button type="button" class="opcao-excluir" @click="excluirAvaliacao(item)">Excluir</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!carregando && avaliacoesFiltradas.length === 0"><td colspan="7" class="sem-resultados">Nenhuma avaliação encontrada.</td></tr>
              <tr v-if="carregando"><td colspan="7" class="sem-resultados">Carregando avaliações...</td></tr>
            </tbody>
          </table>
        </div>
        <div class="rodape-painel">{{ avaliacoesFiltradas.length }} avaliação(ões) encontrada(s) · {{ notas.length }} com nota registrada</div>
      </section>
      <p class="aviso">A média geral considera somente avaliações com nota registrada. A data exibida corresponde à aula vinculada.</p>
    </div>
    <div v-if="menuAbertoId !== null" class="overlay-menu" @click="fecharMenu"></div>
  </div>
</template>

<style scoped>
.pagina-avaliacoes {
  min-height: 100vh;
  background: #F7F8FA;
  color: #1F2937;
  font-family: inherit;
  font-size: 14px;
}

.pagina-avaliacoes *,
.pagina-avaliacoes *::before,
.pagina-avaliacoes *::after {
  box-sizing: border-box;
}

.pagina-avaliacoes button,
.pagina-avaliacoes input,
.pagina-avaliacoes select,
.pagina-avaliacoes textarea {
  font: inherit;
}

button {
  cursor: pointer;
}

/* Faixa superior */
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
  font-weight: 400;
}

/* Indicadores */
.indicadores {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.cartao,
.painel {
  background: #FFFFFF;
  border: 1px solid #E2E5EA;
  border-radius: 12px;
}

.cartao {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 22px;
}

.cartao span {
  color: #6B7280;
  font-size: 14px;
  font-weight: 400;
}

.cartao strong {
  color: #0A1F44;
  font-size: 30px;
  font-weight: 700;
}

.cartao .valor-sucesso {
  color: #2E7D32;
}

.cartao .valor-alerta {
  color: #DC2626;
}

/* Painéis */
.painel {
  margin-bottom: 24px;
  padding: 24px;
  overflow: visible;
}

.topo-painel {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 18px;
}

.topo-painel h2 {
  margin: 0;
  color: #1F2937;
  font-size: 18px;
  font-weight: 600;
  line-height: 1.4;
}

.topo-painel p {
  margin: 6px 0 0;
  color: #6B7280;
  font-size: 13px;
  font-weight: 400;
}

/* Botões */
.botao-primario {
  border: none;
  border-radius: 8px;
  background: #C8102E;
  color: #FFFFFF;
  padding: 11px 16px;
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
}

.botao-primario:hover {
  background: #A90D27;
}

.botao-secundario {
  border: 1px solid #E2E5EA;
  border-radius: 8px;
  background: #FFFFFF;
  color: #0A1F44;
  padding: 10px 15px;
  font-size: 14px;
}

/* Formulário */
.campos {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}

.campos label {
  display: flex;
  flex-direction: column;
  gap: 7px;
  color: #6B7280;
  font-size: 13px;
}

.campo-completo {
  grid-column: 1 / -1;
}

input,
select,
textarea {
  width: 100%;
  min-width: 0;
  border: 1px solid #E2E5EA;
  border-radius: 8px;
  background: #FFFFFF;
  color: #1F2937;
  padding: 11px 12px;
  font-size: 14px;
  font-weight: 400;
}

textarea {
  resize: vertical;
}

input::placeholder,
textarea::placeholder {
  color: #6B7280;
  opacity: 1;
}

input:focus,
select:focus,
textarea:focus {
  outline: 2px solid #0A1F44;
  outline-offset: 1px;
}

.acoes-formulario {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 24px;
}

/* Mensagens */
.erro {
  color: #DC2626;
  font-size: 13px;
  margin-top: 16px;
}

.mensagem {
  background: #E8F5E9;
  color: #2E7D32;
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 20px;
}

/* Filtros */
.filtros {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 230px;
  gap: 12px;
  margin-bottom: 18px;
}

/* Tabela */
.tabela-container {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 12px;
}

.tabela-avaliacoes {
  width: 100%;
  min-width: 880px;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
  color: #1F2937;
}

.tabela-avaliacoes thead {
  background: #F7F8FA;
}

.tabela-avaliacoes th {
  padding: 13px 14px;
  color: #64748B;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 1px solid #E2E5EA;
}

.tabela-avaliacoes td {
  padding: 14px;
  border-bottom: 1px solid #E2E5EA;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 400;
}

.tabela-avaliacoes tbody tr:hover {
  background: #FAFBFD;
}

/* Aluno e observação */
.nome-aluno {
  display: block;
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.observacao {
  display: block;
  max-width: 220px;
  margin-top: 4px;
  color: #6B7280;
  font-size: 12px;
  font-weight: 400;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

/* Notas */
.nota-boa {
  color: #2E7D32;
  font-weight: 600;
}

.nota-baixa {
  color: #DC2626;
  font-weight: 600;
}

/* Desempenho */
.status {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status.satisfatorio {
  background: #DDF5E7;
  color: #008C45;
}

.status.abaixo {
  background: #FEE2E2;
  color: #DC2626;
}

/* Menu de três pontos */
.coluna-acoes {
  text-align: center;
  width: 70px;
}

.menu-acoes {
  position: relative;
  display: inline-block;
  z-index: 1;
}

.menu-acoes.menu-aberto {
  z-index: 101;
}

.botao-tres-pontos {
  border: none;
  background: transparent;
  color: #0A1F44;
  font-size: 20px;
  font-weight: 400;
  padding: 5px 10px;
  border-radius: 6px;
  line-height: 1;
}

.botao-tres-pontos:hover {
  background: #F1F3F6;
}

.opcoes-menu {
  position: absolute;
  top: 100%;
  right: 0;
  z-index: 102;
  min-width: 135px;
  background: #FFFFFF;
  border: 1px solid #E2E5EA;
  border-radius: 8px;
  box-shadow: 0 6px 20px #00000020;
  padding: 5px;
}

.opcoes-menu button {
  display: block;
  width: 100%;
  border: none;
  border-radius: 5px;
  background: transparent;
  color: #0A1F44;
  text-align: left;
  font-size: 14px;
  padding: 10px;
}

.opcoes-menu button:hover {
  background: #F1F3F6;
}

.opcoes-menu .opcao-excluir {
  color: #DC2626;
}

.overlay-menu {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: transparent;
}

/* Rodapé */
.rodape-painel {
  padding-top: 14px;
  color: #6B7280;
  font-size: 12px;
}

.sem-resultados {
  padding: 28px;
  text-align: center;
  color: #6B7280;
}

.aviso {
  color: #6B7280;
  font-size: 12px;
  line-height: 1.6;
}

/* Fonte original do sistema */
.pagina-avaliacoes,
.pagina-avaliacoes h1,
.pagina-avaliacoes h2,
.pagina-avaliacoes p,
.pagina-avaliacoes span,
.pagina-avaliacoes strong,
.pagina-avaliacoes small,
.pagina-avaliacoes label,
.pagina-avaliacoes th,
.pagina-avaliacoes td,
.pagina-avaliacoes button,
.pagina-avaliacoes input,
.pagina-avaliacoes select,
.pagina-avaliacoes textarea {
  font-family: inherit;
}

/* Responsividade */
@media (max-width: 1100px) {
  .indicadores {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 700px) {
  .conteudo {
    padding: 24px 0;
  }

  .indicadores,
  .campos,
  .filtros {
    grid-template-columns: 1fr;
  }

  .campo-completo {
    grid-column: auto;
  }

  .topo-painel {
    align-items: flex-start;
    flex-direction: column;
  }

  .painel {
    padding: 16px;
  }

  .cabecalho-pagina h1 {
    font-size: 23px;
  }
}
</style>
