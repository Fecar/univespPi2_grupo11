<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/services/api'

const cursos = ref([])
const turmas = ref([])
const professores = ref([])
const carregando = ref(false)
const salvando = ref(false)
const erroGeral = ref('')
const erroFormulario = ref('')
const mensagem = ref('')
const pesquisaTurma = ref('')
const pesquisaCurso = ref('')
const mostrarFormulario = ref(false)
const tipoFormulario = ref('turma')
const editandoId = ref(null)
const menuAberto = ref(null)
const formulario = ref({})

const totalTurmas = computed(() => turmas.value.length)
const totalCursos = computed(() => cursos.value.length)
const totalProfessores = computed(() => new Set(turmas.value.map(t => t.professor_id).filter(Boolean)).size)
const turmasSemProfessor = computed(() => turmas.value.filter(t => !t.professor_id).length)
const nomeCurso = id => cursos.value.find(c => c.id === id)?.nome || 'Curso não encontrado'
const nomeProfessor = id => professores.value.find(p => p.id === id)?.nome || 'Professor não encontrado'
const turmasFiltradas = computed(() => {
  const termo = pesquisaTurma.value.trim().toLocaleLowerCase('pt-BR')
  return turmas.value.filter(t => [t.nome, nomeCurso(t.curso_id), nomeProfessor(t.professor_id)]
    .some(v => String(v || '').toLocaleLowerCase('pt-BR').includes(termo)))
})
const cursosFiltrados = computed(() => {
  const termo = pesquisaCurso.value.trim().toLocaleLowerCase('pt-BR')
  return cursos.value.filter(c => [c.nome, c.nivel]
    .some(v => String(v || '').toLocaleLowerCase('pt-BR').includes(termo)))
})

function mensagemErro(e, padrao) {
  const dados = e?.response?.data
  if (e?.response?.status === 401) return 'Sessão expirada ou acesso não autorizado. Faça login novamente.'
  if (e?.response?.status === 409) return 'Não foi possível concluir: o registro pode estar em uso ou já existir.'
  if (e?.response?.status === 422) {
    const detalhe = dados?.detail
    if (detalhe && typeof detalhe === 'object') {
      const campos = Object.values(detalhe).flat().map(String).join('; ')
      if (campos) return `Confira os dados informados: ${campos}`
    }
    return 'Confira os dados informados no formulário.'
  }
  return dados?.message || dados?.msg || padrao
}

async function carregarDados() {
  carregando.value = true
  erroGeral.value = ''
  try {
    const [resCursos, resTurmas, resProfessores] = await Promise.all([
      api.get('/cursos/'),
      api.get('/turmas/'),
      api.get('/professores/')
    ])
    if (![resCursos.data, resTurmas.data, resProfessores.data].every(Array.isArray)) {
      throw new Error('Formato de resposta inesperado da API.')
    }
    cursos.value = resCursos.data
    turmas.value = resTurmas.data
    professores.value = resProfessores.data
  } catch (e) {
    erroGeral.value = mensagemErro(e, e.message || 'Não foi possível carregar os dados do servidor.')
  } finally {
    carregando.value = false
  }
}

function abrirFormulario(tipo, item = null) {
  tipoFormulario.value = tipo
  editandoId.value = item?.id ?? null
  formulario.value = tipo === 'curso'
    ? { nome: item?.nome ?? '', nivel: item?.nivel ?? '' }
    : { nome: item?.nome ?? '', curso_id: item?.curso_id ?? '', professor_id: item?.professor_id ?? '' }
  erroFormulario.value = ''
  mensagem.value = ''
  menuAberto.value = null
  mostrarFormulario.value = true
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelarFormulario() {
  mostrarFormulario.value = false
  editandoId.value = null
  erroFormulario.value = ''
}

async function salvar() {
  erroFormulario.value = ''
  mensagem.value = ''
  const nome = String(formulario.value.nome || '').trim()
  if (!nome) { erroFormulario.value = 'Informe o nome.'; return }
  let dados
  let caminho
  if (tipoFormulario.value === 'curso') {
    const nivel = String(formulario.value.nivel || '').trim()
    if (!nivel) { erroFormulario.value = 'Informe o nível do curso.'; return }
    dados = { nome, nivel }
    caminho = '/cursos/'
  } else {
    const { curso_id, professor_id } = formulario.value
    if (!curso_id || !professor_id) {
      erroFormulario.value = 'Selecione um curso e um professor.'
      return
    }
    dados = { nome, curso_id, professor_id }
    caminho = '/turmas/'
  }
  salvando.value = true
  try {
    const editando = editandoId.value !== null
    if (editando) {
      await api.put(`${caminho}${encodeURIComponent(editandoId.value)}`, dados)
    } else {
      await api.post(caminho, dados)
    }
    cancelarFormulario()
    mensagem.value = `${tipoFormulario.value === 'curso' ? 'Curso' : 'Turma'} ${editando ? 'atualizado(a)' : 'cadastrado(a)'} com sucesso!`
    await carregarDados()
  } catch (e) {
    erroFormulario.value = mensagemErro(e, 'Não foi possível salvar. Tente novamente.')
  } finally {
    salvando.value = false
  }
}

async function excluir(tipo, item) {
  menuAberto.value = null
  const substantivo = tipo === 'curso' ? 'curso' : 'turma'
  if (!window.confirm(`Deseja realmente excluir ${substantivo} "${item.nome}"?`)) return
  erroGeral.value = ''
  mensagem.value = ''
  try {
    await api.delete(`/${tipo === 'curso' ? 'cursos' : 'turmas'}/${encodeURIComponent(item.id)}`)
    mensagem.value = `${tipo === 'curso' ? 'Curso excluído' : 'Turma excluída'} com sucesso!`
    await carregarDados()
  } catch (e) {
    erroGeral.value = mensagemErro(e, 'Não foi possível excluir. Verifique se há registros vinculados.')
  }
}

function alternarMenu(chave) {
  menuAberto.value = menuAberto.value === chave ? null : chave
}

onMounted(carregarDados)
</script>

<template>
  <div class="pagina-turmas" @click.self="menuAberto = null">
    <div class="faixa-superior"></div>
    <div class="conteudo">
      <header class="cabecalho-pagina">
        <h1>Gestão de Turmas e Cursos</h1>
        <p>Cadastre, consulte e organize as turmas e cursos.</p>
      </header>

      <section class="indicadores" aria-label="Indicadores">
        <article class="cartao"><span>Total de turmas</span><strong>{{ totalTurmas }}</strong></article>
        <article class="cartao"><span>Total de cursos</span><strong>{{ totalCursos }}</strong></article>
        <article class="cartao"><span>Professores vinculados</span><strong>{{ totalProfessores }}</strong></article>
        <article class="cartao"><span>Turmas sem professor</span><strong>{{ turmasSemProfessor }}</strong></article>
      </section>

      <p v-if="erroGeral" class="alerta erro" role="alert">{{ erroGeral }}</p>
      <p v-if="mensagem" class="alerta sucesso" role="status">{{ mensagem }}</p>

      <section v-if="mostrarFormulario" class="painel formulario-painel">
        <div class="topo-painel">
          <div>
            <h2>{{ editandoId !== null ? 'Editar' : 'Cadastrar' }} {{ tipoFormulario === 'curso' ? 'curso' : 'turma' }}</h2>
            <p>Os dados serão salvos no banco de dados.</p>
          </div>
          <button type="button" class="botao-secundario" @click="cancelarFormulario">Fechar</button>
        </div>
        <form @submit.prevent="salvar">
          <div class="campos">
            <label>Nome {{ tipoFormulario === 'curso' ? 'do curso' : 'da turma' }} *
              <input v-model="formulario.nome" maxlength="255" required placeholder="Informe o nome" />
            </label>
            <template v-if="tipoFormulario === 'curso'">
              <label>Nível *
                <input v-model="formulario.nivel" maxlength="255" required placeholder="Ex.: Iniciante" />
              </label>
            </template>
            <template v-else>
              <label>Curso *
                <select v-model="formulario.curso_id" required>
                  <option value="" disabled>Selecione um curso</option>
                  <option v-for="curso in cursos" :key="curso.id" :value="curso.id">{{ curso.nome }} — {{ curso.nivel }}</option>
                </select>
              </label>
              <label>Professor responsável *
                <select v-model="formulario.professor_id" required>
                  <option value="" disabled>Selecione um professor</option>
                  <option v-for="professor in professores" :key="professor.id" :value="professor.id">{{ professor.nome }}</option>
                </select>
              </label>
            </template>
          </div>
          <p v-if="tipoFormulario === 'turma' && !cursos.length" class="dica">Cadastre um curso antes de criar uma turma.</p>
          <p v-if="tipoFormulario === 'turma' && !professores.length" class="dica">Cadastre um professor antes de criar uma turma.</p>
          <p v-if="erroFormulario" class="erro-texto" role="alert">{{ erroFormulario }}</p>
          <div class="acoes-formulario">
            <button type="button" class="botao-secundario" @click="cancelarFormulario">Cancelar</button>
            <button type="submit" class="botao-primario" :disabled="salvando || (tipoFormulario === 'turma' && (!cursos.length || !professores.length))">
              {{ salvando ? 'Salvando...' : editandoId !== null ? 'Salvar alterações' : 'Cadastrar ' + (tipoFormulario === 'curso' ? 'curso' : 'turma') }}
            </button>
          </div>
        </form>
      </section>

      <section class="painel">
        <div class="topo-painel">
          <div><h2>Turmas cadastradas</h2><p>Consulte e gerencie as turmas da escola.</p></div>
          <button type="button" class="botao-primario" @click="abrirFormulario('turma')">+ Nova turma</button>
        </div>
        <div class="filtros">
          <input v-model="pesquisaTurma" type="search" placeholder="Pesquisar por turma, curso ou professor..." aria-label="Pesquisar turmas" />
          <button type="button" class="botao-secundario" :disabled="carregando" @click="carregarDados">{{ carregando ? 'Atualizando...' : 'Atualizar dados' }}</button>
        </div>
        <div class="tabela-container">
          <table class="tabela">
            <thead><tr><th>Nome da turma</th><th>Curso</th><th>Professor</th><th class="coluna-acoes">Ações</th></tr></thead>
            <tbody>
              <tr v-for="turma in turmasFiltradas" :key="turma.id">
                <td><strong class="nome-registro">{{ turma.nome }}</strong></td>
                <td class="texto-secundario">{{ nomeCurso(turma.curso_id) }}</td>
                <td>{{ nomeProfessor(turma.professor_id) }}</td>
                <td class="coluna-acoes">
                  <div class="menu-acoes">
                    <button type="button" class="botao-tres-pontos" :aria-label="'Ações da turma ' + turma.nome" :aria-expanded="menuAberto === 'turma-' + turma.id" @click.stop="alternarMenu('turma-' + turma.id)">⋮</button>
                    <div v-if="menuAberto === 'turma-' + turma.id" class="opcoes-menu">
                      <button type="button" @click="abrirFormulario('turma', turma)">Editar</button>
                      <button type="button" class="opcao-excluir" @click="excluir('turma', turma)">Excluir</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!turmasFiltradas.length"><td colspan="4" class="sem-resultados">{{ carregando ? 'Carregando turmas...' : 'Nenhuma turma encontrada.' }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="rodape-painel">{{ turmasFiltradas.length }} turma(s) encontrada(s)</div>
      </section>

      <section class="painel">
        <div class="topo-painel">
          <div><h2>Cursos cadastrados</h2><p>Gerencie os cursos e níveis disponíveis.</p></div>
          <button type="button" class="botao-primario" @click="abrirFormulario('curso')">+ Novo curso</button>
        </div>
        <div class="filtros filtro-unico">
          <input v-model="pesquisaCurso" type="search" placeholder="Pesquisar por curso ou nível..." aria-label="Pesquisar cursos" />
        </div>
        <div class="tabela-container">
          <table class="tabela">
            <thead><tr><th>Nome do curso</th><th>Nível</th><th>Turmas vinculadas</th><th class="coluna-acoes">Ações</th></tr></thead>
            <tbody>
              <tr v-for="curso in cursosFiltrados" :key="curso.id">
                <td><strong class="nome-registro">{{ curso.nome }}</strong></td>
                <td class="texto-secundario">{{ curso.nivel }}</td>
                <td>{{ turmas.filter(t => t.curso_id === curso.id).length }}</td>
                <td class="coluna-acoes">
                  <div class="menu-acoes">
                    <button type="button" class="botao-tres-pontos" :aria-label="'Ações do curso ' + curso.nome" :aria-expanded="menuAberto === 'curso-' + curso.id" @click.stop="alternarMenu('curso-' + curso.id)">⋮</button>
                    <div v-if="menuAberto === 'curso-' + curso.id" class="opcoes-menu">
                      <button type="button" @click="abrirFormulario('curso', curso)">Editar</button>
                      <button type="button" class="opcao-excluir" @click="excluir('curso', curso)">Excluir</button>
                    </div>
                  </div>
                </td>
              </tr>
              <tr v-if="!cursosFiltrados.length"><td colspan="4" class="sem-resultados">{{ carregando ? 'Carregando cursos...' : 'Nenhum curso encontrado.' }}</td></tr>
            </tbody>
          </table>
        </div>
        <div class="rodape-painel">{{ cursosFiltrados.length }} curso(s) encontrado(s)</div>
      </section>
      <p class="aviso">Dados carregados da API. Horários, ocupação e situação das turmas ainda não fazem parte do cadastro de turmas disponibilizado pelo backend.</p>
    </div>
    <div v-if="menuAberto !== null" class="overlay-menu" @click="menuAberto = null"></div>
  </div>
</template>

<style scoped>
.pagina-turmas{min-height:100vh;background:#F7F8FA;color:#1F2937;font-family:inherit;font-size:14px}
.pagina-turmas *{box-sizing:border-box}
button,input,select{font:inherit}
button{cursor:pointer}
button:disabled{opacity:.6;cursor:not-allowed}
.faixa-superior{height:6px;background:#0A1F44}
.conteudo{width:min(1200px,94%);margin:0 auto;padding:30px 0 36px}
.cabecalho-pagina{margin-bottom:24px}
.cabecalho-pagina h1{margin:0 0 8px;color:#C8102E;font-size:26px;line-height:1.25}
.cabecalho-pagina p{margin:0;color:#0A1F44}
.indicadores{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:16px;margin-bottom:24px}
.cartao,.painel{background:#fff;border:1px solid #E2E5EA;border-radius:12px}
.cartao{display:flex;flex-direction:column;gap:12px;padding:22px}
.cartao span{color:#6B7280}
.cartao strong{color:#0A1F44;font-size:30px}
.painel{margin-bottom:24px;padding:24px;overflow:visible}
.topo-painel{display:flex;justify-content:space-between;align-items:center;gap:16px;margin-bottom:18px}
.topo-painel h2{margin:0;color:#1F2937;font-size:18px}
.topo-painel p{margin:6px 0 0;color:#6B7280;font-size:13px}
.botao-primario{border:0;border-radius:8px;background:#C8102E;color:white;padding:11px 16px;font-weight:600;white-space:nowrap}
.botao-primario:not(:disabled):hover{background:#A90D27}
.botao-secundario{border:1px solid #E2E5EA;border-radius:8px;background:white;color:#0A1F44;padding:10px 15px}
.botao-secundario:not(:disabled):hover{background:#F7F8FA}
.campos{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}
.campos label{display:flex;flex-direction:column;gap:7px;color:#6B7280;font-size:13px}
input,select{width:100%;min-width:0;border:1px solid #E2E5EA;border-radius:8px;background:#fff;color:#1F2937;padding:11px 12px}
input:focus,select:focus{outline:2px solid #0A1F44;outline-offset:1px}
.acoes-formulario{display:flex;justify-content:flex-end;gap:12px;flex-wrap:wrap;margin-top:24px}
.alerta{padding:14px;border-radius:8px;margin:0 0 20px}
.alerta.erro{background:#FDECEC;color:#991B1B}
.alerta.sucesso{background:#E8F5E9;color:#2E7D32}
.erro-texto{color:#DC2626;font-size:13px;margin-top:16px}
.dica{color:#8A5200;font-size:13px}
.filtros{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:12px;margin-bottom:14px}
.filtro-unico{grid-template-columns:1fr}
.tabela-container{width:100%;overflow-x:auto;padding-bottom:90px;margin-bottom:-75px}
.tabela{width:100%;min-width:650px;border-collapse:collapse;text-align:left;font-size:13px}
.tabela th{padding:13px 14px;background:#F7F8FA;color:#64748B;font-size:11px;font-weight:600;border-bottom:1px solid #E2E5EA}
.tabela td{padding:14px;border-bottom:1px solid #E2E5EA;vertical-align:middle}
.tabela tbody tr:hover{background:#FAFBFD}
.nome-registro{color:#0A1F44;font-weight:600}
.texto-secundario{color:#6B7280}
.coluna-acoes{text-align:center;width:85px}
.menu-acoes{position:relative;display:inline-block}
.botao-tres-pontos{border:0;background:transparent;color:#0A1F44;font-size:22px;padding:5px 12px;border-radius:6px}
.botao-tres-pontos:hover{background:#F1F3F6}
.opcoes-menu{position:absolute;top:100%;right:0;z-index:102;min-width:135px;background:#fff;border:1px solid #E2E5EA;border-radius:8px;box-shadow:0 6px 20px #0002;padding:5px}
.opcoes-menu button{display:block;width:100%;border:0;background:transparent;border-radius:5px;text-align:left;padding:10px;color:#0A1F44}
.opcoes-menu button:hover{background:#F1F3F6}
.opcoes-menu .opcao-excluir{color:#DC2626}
.overlay-menu{position:fixed;inset:0;z-index:50;background:transparent}
.painel:has(.opcoes-menu){position:relative;z-index:60}
.sem-resultados{text-align:center;padding:28px!important;color:#6B7280}
.rodape-painel{padding-top:14px;color:#6B7280;font-size:12px}
.aviso{color:#6B7280;font-size:12px;line-height:1.6}
@media(max-width:1100px){.indicadores{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:700px){.conteudo{padding:24px 0}.indicadores,.campos,.filtros{grid-template-columns:1fr}.topo-painel{align-items:flex-start;flex-direction:column}.painel{padding:16px}.cabecalho-pagina h1{font-size:23px}}
</style>
