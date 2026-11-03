<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const alunos = ref([])
const pesquisa = ref('')
const carregando = ref(false)
const salvando = ref(false)
const excluindoId = ref(null)
const mostrarFormulario = ref(false)
const editandoId = ref(null)
const menuAbertoId = ref(null)
const erro = ref('')
const erroFormulario = ref('')
const mensagem = ref('')

const formularioVazio = () => ({ nome: '', email: '', cpf: '' })
const formulario = ref(formularioVazio())

const totalAlunos = computed(() => alunos.value.length)
const alunosComEmail = computed(() => alunos.value.filter(a => Boolean(a.email)).length)
const alunosComCpf = computed(() => alunos.value.filter(a => Boolean(a.cpf)).length)
const alunosFiltrados = computed(() => {
  const termo = pesquisa.value.trim().toLocaleLowerCase('pt-BR')
  return alunos.value.filter(aluno =>
    [aluno.nome, aluno.email, aluno.cpf]
      .some(valor => String(valor ?? '').toLocaleLowerCase('pt-BR').includes(termo))
  )
})

function mensagemErro(error, padrao) {
  const status = error?.response?.status
  const dados = error?.response?.data
  if (status === 401) return 'Sessão expirada ou acesso não autorizado. Faça login novamente.'
  if (status === 409) return 'Não foi possível concluir: o registro pode já existir ou estar em uso.'
  if (status === 422 || status === 400) {
    const detalhe = dados?.detail
    if (typeof detalhe === 'string') return detalhe
    return dados?.message || 'Confira os campos informados.'
  }
  return dados?.message || (error?.response ? padrao : 'Não foi possível conectar ao servidor. Verifique se o backend está ativo.')
}

async function carregarAlunos() {
  carregando.value = true
  erro.value = ''
  try {
    const resposta = await api.get('/alunos/')
    if (!Array.isArray(resposta.data)) throw new Error('Formato de resposta inesperado')
    alunos.value = resposta.data
  } catch (error) {
    erro.value = mensagemErro(error, 'Não foi possível carregar os alunos.')
    if (!error?.response) console.error('Erro ao carregar alunos:', error)
  } finally {
    carregando.value = false
  }
}

function abrirCadastro() {
  editandoId.value = null
  formulario.value = formularioVazio()
  mostrarFormulario.value = true
  menuAbertoId.value = null
  erroFormulario.value = ''
  mensagem.value = ''
}

function editarAluno(aluno) {
  editandoId.value = aluno.id
  formulario.value = {
    nome: aluno.nome || '',
    email: aluno.email || '',
    cpf: aluno.cpf || ''
  }
  mostrarFormulario.value = true
  menuAbertoId.value = null
  erroFormulario.value = ''
  mensagem.value = ''
}

function cancelar() {
  mostrarFormulario.value = false
  editandoId.value = null
  erroFormulario.value = ''
}

async function salvarAluno() {
  if (salvando.value) return
  erroFormulario.value = ''
  mensagem.value = ''
  const dados = {
    nome: formulario.value.nome.trim(),
    email: formulario.value.email.trim(),
    cpf: formulario.value.cpf.replace(/\D/g, '')
  }
  if (!dados.nome || !dados.email || !dados.cpf) {
    erroFormulario.value = 'Preencha nome, e-mail e CPF.'
    return
  }
  if (!/^\d{11}$/.test(dados.cpf)) {
    erroFormulario.value = 'O CPF deve conter 11 números.'
    return
  }
  const cpfDuplicado = alunos.value.some(a =>
    String(a.id) !== String(editandoId.value) && String(a.cpf || '').replace(/\D/g, '') === dados.cpf
  )
  if (cpfDuplicado) {
    erroFormulario.value = 'Já existe um aluno cadastrado com esse CPF.'
    return
  }
  salvando.value = true
  try {
    const edicao = editandoId.value !== null
    if (edicao) {
      await api.put(`/alunos/${encodeURIComponent(editandoId.value)}`, dados)
    } else {
      await api.post('/alunos/', dados)
    }
    await carregarAlunos()
    if (erro.value) {
      erroFormulario.value = 'Cadastro salvo, mas não foi possível atualizar a lista. Clique em Atualizar dados.'
      return
    }
    cancelar()
    mensagem.value = edicao ? 'Aluno atualizado com sucesso!' : 'Aluno cadastrado com sucesso!'
  } catch (error) {
    erroFormulario.value = mensagemErro(error, 'Não foi possível salvar o aluno.')
  } finally {
    salvando.value = false
  }
}

async function excluirAluno(aluno) {
  menuAbertoId.value = null
  if (!window.confirm(`Deseja realmente excluir o aluno "${aluno.nome}"?`)) return
  if (excluindoId.value !== null) return
  excluindoId.value = aluno.id
  erro.value = ''
  mensagem.value = ''
  try {
    await api.delete(`/alunos/${encodeURIComponent(aluno.id)}`)
    if (String(editandoId.value) === String(aluno.id)) cancelar()
    await carregarAlunos()
    if (!erro.value) mensagem.value = 'Aluno excluído com sucesso!'
  } catch (error) {
    erro.value = mensagemErro(error, 'Não foi possível excluir o aluno.')
  } finally {
    excluindoId.value = null
  }
}

function alternarMenu(id) {
  menuAbertoId.value = menuAbertoId.value === id ? null : id
}
function fecharMenu() { menuAbertoId.value = null }
function formatarCpf(cpf) {
  const digitos = String(cpf ?? '').replace(/\D/g, '')
  return /^\d{11}$/.test(digitos)
    ? digitos.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
    : (cpf || 'Não informado')
}
onMounted(carregarAlunos)
</script>

<template>
  <div class="pagina-alunos">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <h1>Gestão de Alunos</h1>
        <p>Cadastre, consulte e organize os alunos.</p>
      </header>

      <section class="indicadores" aria-label="Resumo de alunos">
        <article class="cartao"><span>Total de alunos</span><strong>{{ totalAlunos }}</strong></article>
        <article class="cartao"><span>Com e-mail cadastrado</span><strong>{{ alunosComEmail }}</strong></article>
        <article class="cartao"><span>Com CPF cadastrado</span><strong>{{ alunosComCpf }}</strong></article>
      </section>

      <p v-if="mensagem" class="mensagem" role="status">{{ mensagem }}</p>
      <p v-if="erro" class="erro" role="alert">{{ erro }}</p>

      <section v-if="mostrarFormulario" class="painel formulario-painel">
        <div class="topo-painel">
          <div>
            <h2>{{ editandoId !== null ? 'Editar aluno' : 'Cadastrar novo aluno' }}</h2>
            <p>Preencha os dados do aluno.</p>
          </div>
          <button type="button" class="botao-secundario" :disabled="salvando" @click="cancelar">Fechar</button>
        </div>
        <form @submit.prevent="salvarAluno">
          <div class="campos">
            <label>Nome completo *
              <input v-model="formulario.nome" name="nome" type="text" maxlength="255" required placeholder="Nome completo do aluno" />
            </label>
            <label>E-mail *
              <input v-model="formulario.email" name="email" type="email" maxlength="255" required placeholder="aluno@exemplo.com" />
            </label>
            <label>CPF *
              <input v-model="formulario.cpf" name="cpf" type="text" inputmode="numeric" maxlength="14" required placeholder="000.000.000-00" />
            </label>
          </div>
          <p v-if="erroFormulario" class="erro" role="alert">{{ erroFormulario }}</p>
          <div class="acoes-formulario">
            <button type="button" class="botao-secundario" :disabled="salvando" @click="cancelar">Cancelar</button>
            <button type="submit" class="botao-primario" :disabled="salvando">
              {{ salvando ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Cadastrar aluno' }}
            </button>
          </div>
        </form>
      </section>

      <section class="painel">
        <div class="topo-painel">
          <div><h2>Alunos cadastrados</h2><p>Consulte e gerencie os registros dos alunos.</p></div>
          <button type="button" class="botao-primario" @click="abrirCadastro">+ Novo aluno</button>
        </div>
        <div class="filtros">
          <input v-model="pesquisa" name="pesquisa" type="search" placeholder="Pesquisar por nome, e-mail ou CPF..." aria-label="Pesquisar alunos" />
          <button type="button" class="botao-secundario" :disabled="carregando" @click="carregarAlunos">
            {{ carregando ? 'Atualizando...' : 'Atualizar dados' }}
          </button>
        </div>
        <div class="tabela-container">
          <table class="tabela-alunos">
            <thead><tr><th>Nome</th><th>E-mail</th><th>CPF</th><th class="coluna-acoes">Ações</th></tr></thead>
            <tbody>
              <tr v-for="aluno in alunosFiltrados" :key="aluno.id">
                <td><strong class="nome-aluno">{{ aluno.nome }}</strong></td>
                <td><span class="email-aluno">{{ aluno.email }}</span></td>
                <td>{{ formatarCpf(aluno.cpf) }}</td>
                <td class="coluna-acoes">
                  <div class="menu-acoes" :class="{ 'menu-aberto': menuAbertoId === aluno.id }">
                    <button type="button" class="botao-tres-pontos" :aria-label="'Ações de ' + aluno.nome" :aria-expanded="menuAbertoId === aluno.id" @click.stop="alternarMenu(aluno.id)">⋮</button>
                    <div v-if="menuAbertoId === aluno.id" class="opcoes-menu">
                      <button type="button" @click="editarAluno(aluno)">Editar</button>
                      <button type="button" class="opcao-excluir" :disabled="excluindoId === aluno.id" @click="excluirAluno(aluno)">Excluir</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!carregando && alunosFiltrados.length === 0">
                <td colspan="4" class="sem-resultados">{{ pesquisa ? 'Nenhum aluno corresponde à pesquisa.' : 'Nenhum aluno cadastrado.' }}</td>
              </tr>
              <tr v-if="carregando"><td colspan="4" class="sem-resultados">Carregando alunos...</td></tr>
            </tbody>
          </table>
        </div>
        <div class="rodape-painel">{{ alunosFiltrados.length }} aluno(s) encontrado(s)</div>
      </section>
      <p class="aviso">Os dados exibidos são consultados na API. Turma, telefone e situação não fazem parte do cadastro de alunos disponível atualmente no backend.</p>
    </div>
    <div v-if="menuAbertoId !== null" class="overlay-menu" @click="fecharMenu"></div>
  </div>
</template>

<style scoped>
.pagina-alunos {
  min-height: 100vh;
  background: #F7F8FA;
  color: #1F2937;
  font-family: inherit;
  font-size: 14px;
}

.pagina-alunos *,
.pagina-alunos *::before,
.pagina-alunos *::after {
  box-sizing: border-box;
}

.pagina-alunos button,
.pagina-alunos input,
.pagina-alunos select {
  font: inherit;
}

button {
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
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

input,
select {
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

input::placeholder {
  color: #6B7280;
  opacity: 1;
}

input:focus,
select:focus {
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

/* Pesquisa e filtro */
.filtros {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 160px;
  gap: 12px;
  margin-bottom: 18px;
}

/* Tabela */
.tabela-container {
  width: 100%;
  overflow-x: auto;
  padding-bottom: 12px;
}

.tabela-alunos {
  width: 100%;
  min-width: 680px;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
  color: #1F2937;
}

.tabela-alunos thead {
  background: #F7F8FA;
}

.tabela-alunos th {
  padding: 13px 14px;
  color: #64748B;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 1px solid #E2E5EA;
}

.tabela-alunos td {
  padding: 14px;
  border-bottom: 1px solid #E2E5EA;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 400;
}

.tabela-alunos tbody tr:hover {
  background: #FAFBFD;
}

/* Dados do aluno */
.nome-aluno {
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.email-aluno {
  display: block;
  color: #1F2937;
  font-size: 13px;
}

.texto-secundario {
  display: block;
  margin-top: 4px;
  color: #6B7280;
  font-size: 12px;
  font-weight: 400;
}

/* Situação */
.status {
  display: inline-block;
  padding: 5px 10px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.status.ativo {
  background: #DDF5E7;
  color: #008C45;
}

.status.inativo {
  background: #E2E5EA;
  color: #64748B;
}

/* Menu de ações */
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
.pagina-alunos,
.pagina-alunos h1,
.pagina-alunos h2,
.pagina-alunos p,
.pagina-alunos span,
.pagina-alunos strong,
.pagina-alunos small,
.pagina-alunos label,
.pagina-alunos th,
.pagina-alunos td,
.pagina-alunos button,
.pagina-alunos input,
.pagina-alunos select {
  font-family: inherit;
}

/* Responsividade */
@media (max-width: 900px) {
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


/* Ajuste para o botão Atualizar dados ocupar a segunda coluna dos filtros */
.filtros .botao-secundario { white-space: nowrap; }
.botao-primario:disabled, .botao-secundario:disabled { opacity: .6; cursor: not-allowed; }
</style>
