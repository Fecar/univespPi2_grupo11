from apiflask import Schema
from apiflask.fields import DateTime, Integer, String, Date


class ProfessorIn(Schema):
    nome = String(required=True)
    email = String(required=True)
    cpf = String(required=True)


class ProfessorOut(Schema):
    id = String()
    nome = String()
    email = String()
    cpf = String()


class ProfessorOutId(Schema):

    id = String()
    nome = String()
    data_nascimento = Date()
    cpf = String()
    email = String()
    telefone = String()
    celular_whatsapp = String()

    cep = String()
    logradouro = String()
    bairro = String()
    cidade_uf = String()

    graduacao_curso = String()
    instituicao_ensino = String()
    ano_conclusao = Integer()
    pos_graduacao = String()

    data_cadastro = DateTime()
    privilegio = String()
