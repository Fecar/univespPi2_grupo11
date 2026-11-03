<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const professores = ref([])
const turmas = ref([])
const pesquisa = ref('')
const mostrarFormulario = ref(false)
const editandoId = ref(null)
const menuAbertoId = ref(null)
const carregando = ref(false)
const salvando = ref(false)
const erro = ref('')
const mensagem = ref('')
const formularioVazio = () => ({ nome: '', email: '', cpf: '', senha: '', telefone: '', celular_whatsapp: '', data_nascimento: '', area_atuacao: '' })
const formulario = ref(formularioVazio())
const totalProfessores = computed(() => professores.value.length)
const professoresComTurmas = computed(() => professores.value.filter(p => turmas.value.some(t => String(t.professor_id) === String(p.id))).length)
const professoresSemTurmas = computed(() => totalProfessores.value - professoresComTurmas.value)
const professoresFiltrados = computed(() => {
  const termo = pesquisa.value.trim().toLocaleLowerCase('pt-BR')
  return professores.value.filter(p => [p.nome, p.email, p.cpf, nomesTurmas(p.id)].some(v => String(v || '').toLocaleLowerCase('pt-BR').includes(termo)))
})
function nomesTurmas(id) {
  return turmas.value.filter(t => String(t.professor_id) === String(id)).map(t => t.nome).join(', ') || 'Nenhuma turma vinculada'
}
function mensagemErro(e, padrao) {
  const status = e?.response?.status
  const dados = e?.response?.data
  if (status === 401) return 'Sessão expirada ou acesso não autorizado. Entre novamente.'
  if (status === 409) return 'Não foi possível concluir: o registro pode estar em uso ou já existir.'
  if (status === 422) return 'Confira os campos informados. O backend rejeitou os dados enviados.'
  return dados?.message || padrao
}
async function carregarDados() {
  carregando.value = true
  erro.value = ''
  try {
    const [resProfessores, resTurmas] = await Promise.all([api.get('/professores/'), api.get('/turmas/')])
    professores.value = Array.isArray(resProfessores.data) ? resProfessores.data : []
    turmas.value = Array.isArray(resTurmas.data) ? resTurmas.data : []
  } catch (e) {
    erro.value = mensagemErro(e, 'Não foi possível carregar os professores e as turmas.')
  } finally { carregando.value = false }
}
function abrirCadastro() {
  editandoId.value = null
  formulario.value = formularioVazio()
  erro.value = ''; mensagem.value = ''; menuAbertoId.value = null
  mostrarFormulario.value = true
}
async function editarProfessor(p) {
  erro.value = ''; mensagem.value = ''; menuAbertoId.value = null
  editandoId.value = p.id
  formulario.value = { ...formularioVazio(), nome: p.nome || '', email: p.email || '', cpf: p.cpf || '' }
  mostrarFormulario.value = true
  try {
    const { data } = await api.get(`/professores/${encodeURIComponent(p.id)}`)
    if (editandoId.value !== p.id) return
    formulario.value = { ...formulario.value, telefone: data.telefone || '', celular_whatsapp: data.celular_whatsapp || '', data_nascimento: data.data_nascimento || '' }
  } catch (e) {
    erro.value = 'Não foi possível consultar os detalhes. Confira os dados antes de salvar.'
  }
}
function cancelar() { mostrarFormulario.value = false; editandoId.value = null; erro.value = '' }
function alternarMenu(id) { menuAbertoId.value = menuAbertoId.value === id ? null : id }
function fecharMenu() { menuAbertoId.value = null }
async function salvarProfessor() {
  if (salvando.value) return
  erro.value = ''; mensagem.value = ''
  const f = formulario.value
  const cpf = String(f.cpf || '').replace(/\D/g, '')
  if (!f.nome.trim() || !f.email.trim() || cpf.length !== 11) { erro.value = 'Informe nome, e-mail e CPF com 11 dígitos.'; return }
  if (editandoId.value === null && !f.senha) { erro.value = 'Informe uma senha para o novo professor.'; return }
  const dados = { nome: f.nome.trim(), email: f.email.trim(), cpf }
  if (f.senha) dados.senha = f.senha
  if (f.telefone.trim()) dados.telefone = f.telefone.trim()
  if (f.celular_whatsapp.trim()) dados.celular_whatsapp = f.celular_whatsapp.trim()
  if (f.data_nascimento) dados.data_nascimento = f.data_nascimento
  salvando.value = true
  try {
    if (editandoId.value === null) await api.post('/professores/', dados)
    else await api.put(`/professores/${encodeURIComponent(editandoId.value)}`, dados)
    const foiEdicao = editandoId.value !== null
    cancelar()
    await carregarDados()
    mensagem.value = foiEdicao ? 'Professor atualizado com sucesso!' : 'Professor cadastrado com sucesso!'
  } catch (e) { erro.value = mensagemErro(e, 'Não foi possível salvar o professor.') }
  finally { salvando.value = false }
}
async function excluirProfessor(p) {
  fecharMenu()
  if (!window.confirm(`Deseja realmente excluir o professor "${p.nome}"? Isso pode afetar seu acesso ao sistema.`)) return
  erro.value = ''; mensagem.value = ''
  try {
    await api.delete(`/professores/${encodeURIComponent(p.id)}`)
    if (editandoId.value === p.id) cancelar()
    await carregarDados()
    mensagem.value = 'Professor excluído com sucesso!'
  } catch (e) { erro.value = mensagemErro(e, 'Não foi possível excluir o professor. Ele pode estar vinculado a uma turma.') }
}
onMounted(carregarDados)
</script>

<template>
  <div class="pagina-professores">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <h1>Gestão de Professores</h1>
        <p>Cadastre, consulte e organize os professores da escola.</p>
      </header>
      <section class="indicadores" aria-label="Resumo de professores">
        <article class="cartao"><span>Total de professores</span><strong>{{ totalProfessores }}</strong></article>
        <article class="cartao"><span>Com turmas vinculadas</span><strong>{{ professoresComTurmas }}</strong></article>
        <article class="cartao"><span>Sem turmas vinculadas</span><strong>{{ professoresSemTurmas }}</strong></article>
      </section>
      <p v-if="mensagem" class="mensagem" role="status">{{ mensagem }}</p>
      <p v-if="erro && !mostrarFormulario" class="erro" role="alert">{{ erro }}</p>
      <section v-if="mostrarFormulario" class="painel formulario-painel">
        <div class="topo-painel">
          <div><h2>{{ editandoId !== null ? 'Editar professor' : 'Cadastrar novo professor' }}</h2><p>Preencha os dados do professor. A senha é necessária para novos cadastros.</p></div>
          <button type="button" class="botao-secundario" @click="cancelar">Fechar</button>
        </div>
        <form @submit.prevent="salvarProfessor">
          <div class="campos">
            <label>Nome completo *<input name="nome" v-model="formulario.nome" type="text" maxlength="255" required placeholder="Nome completo" /></label>
            <label>E-mail *<input name="email" v-model="formulario.email" type="email" maxlength="255" required placeholder="professor@exemplo.com" /></label>
            <label>CPF *<input name="cpf" v-model="formulario.cpf" type="text" inputmode="numeric" maxlength="14" required placeholder="000.000.000-00" /></label>
            <label>Senha {{ editandoId === null ? '*' : '(opcional, conforme regras do backend)' }}<input name="senha" v-model="formulario.senha" type="password" autocomplete="new-password" :required="editandoId === null" placeholder="Digite uma senha" /></label>
            <label>Telefone<input name="telefone" v-model="formulario.telefone" type="tel" maxlength="30" placeholder="(11) 9999-9999" /></label>
            <label>Celular / WhatsApp<input name="celular_whatsapp" v-model="formulario.celular_whatsapp" type="tel" maxlength="30" placeholder="(11) 99999-9999" /></label>
            <label>Data de nascimento<input name="data_nascimento" v-model="formulario.data_nascimento" type="date" /></label>
          </div>
          <p v-if="editandoId !== null" class="aviso">A senha não é recuperada pela API. Se a atualização exigir senha, o backend precisará permitir edição sem alterá-la ou disponibilizar uma rota específica.</p>
          <p v-if="erro" class="erro" role="alert">{{ erro }}</p>
          <div class="acoes-formulario">
            <button type="button" class="botao-secundario" :disabled="salvando" @click="cancelar">Cancelar</button>
            <button type="submit" class="botao-primario" :disabled="salvando">{{ salvando ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Cadastrar professor' }}</button>
          </div>
        </form>
      </section>
      <section class="painel">
        <div class="topo-painel">
          <div><h2>Professores cadastrados</h2><p>Consulte e gerencie os registros dos professores.</p></div>
          <button type="button" class="botao-primario" @click="abrirCadastro">+ Novo professor</button>
        </div>
        <div class="filtros" style="grid-template-columns: minmax(0,1fr) auto">
          <input name="pesquisa" v-model="pesquisa" type="search" placeholder="Pesquisar por nome, e-mail, CPF ou turma..." aria-label="Pesquisar professores" />
          <button type="button" class="botao-secundario" :disabled="carregando" @click="carregarDados">Atualizar dados</button>
        </div>
        <div class="tabela-container">
          <table class="tabela-professores">
            <thead><tr><th>Professor</th><th>Contato</th><th>CPF</th><th>Turmas vinculadas</th><th class="coluna-acoes">Ações</th></tr></thead>
            <tbody>
              <tr v-for="p in professoresFiltrados" :key="p.id">
                <td><strong class="nome-professor">{{ p.nome }}</strong></td>
                <td><span class="email-professor">{{ p.email }}</span></td>
                <td>{{ p.cpf || 'Não informado' }}</td>
                <td>{{ nomesTurmas(p.id) }}</td>
                <td class="coluna-acoes">
                  <div class="menu-acoes" :class="{ 'menu-aberto': menuAbertoId === p.id }">
                    <button type="button" class="botao-tres-pontos" :aria-label="'Ações de ' + p.nome" :aria-expanded="menuAbertoId === p.id" @click.stop="alternarMenu(p.id)">⋮</button>
                    <div v-if="menuAbertoId === p.id" class="opcoes-menu">
                      <button type="button" @click="editarProfessor(p)">Editar</button>
                      <button type="button" class="opcao-excluir" @click="excluirProfessor(p)">Excluir</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!carregando && professoresFiltrados.length === 0"><td colspan="5" class="sem-resultados">Nenhum professor encontrado.</td></tr>
              <tr v-if="carregando"><td colspan="5" class="sem-resultados">Carregando professores...</td></tr>
            </tbody>
          </table>
        </div>
        <div class="rodape-painel">{{ professoresFiltrados.length }} professor(es) encontrado(s)</div>
      </section>
      <p class="aviso">Os dados exibidos são consultados diretamente na API. A atribuição de turmas é feita em Gestão de Turmas e Cursos.</p>
    </div>
    <div v-if="menuAbertoId !== null" class="overlay-menu" @click="fecharMenu"></div>
  </div>
</template>

<style scoped>
.pagina-professores {
  min-height: 100vh;
  background: #F7F8FA;
  color: #1F2937;
  font-family: inherit;
  font-size: 14px;
}

.pagina-professores *,
.pagina-professores *::before,
.pagina-professores *::after {
  box-sizing: border-box;
}

.pagina-professores button,
.pagina-professores input,
.pagina-professores select {
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

/* Área principal */
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

.tabela-professores {
  width: 100%;
  min-width: 760px;
  border-collapse: collapse;
  text-align: left;
  font-size: 13px;
  color: #1F2937;
}

.tabela-professores thead {
  background: #F7F8FA;
}

.tabela-professores th {
  padding: 13px 14px;
  color: #64748B;
  font-size: 11px;
  font-weight: 600;
  white-space: nowrap;
  border-bottom: 1px solid #E2E5EA;
}

.tabela-professores td {
  padding: 14px;
  border-bottom: 1px solid #E2E5EA;
  vertical-align: middle;
  font-size: 13px;
  font-weight: 400;
}

.tabela-professores tbody tr:hover {
  background: #FAFBFD;
}

/* Dados do professor */
.nome-professor {
  color: #0A1F44;
  font-size: 13px;
  font-weight: 600;
}

.email-professor {
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

/* Ações */
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
  padding: 5px;
  background: #FFFFFF;
  border: 1px solid #E2E5EA;
  border-radius: 8px;
  box-shadow: 0 6px 20px #00000020;
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
.pagina-professores,
.pagina-professores h1,
.pagina-professores h2,
.pagina-professores p,
.pagina-professores span,
.pagina-professores strong,
.pagina-professores small,
.pagina-professores label,
.pagina-professores th,
.pagina-professores td,
.pagina-professores button,
.pagina-professores input,
.pagina-professores select {
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
</style>
