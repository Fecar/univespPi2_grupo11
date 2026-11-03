from apiflask import Schema
from apiflask.fields import String, DateTime, Float


class AulaIn(Schema):
    nome = String(required=True)
    assunto = String()
    materia = String()
    data_hora = DateTime(required=True)
    turma_id = String(required=True)


class AulaOut(Schema):
    id = String()
    nome = String()
    assunto = String()
    materia = String()
    data_hora = DateTime()
    turma_id = String()


class AvaliacaoIn(Schema):
    aluno_id = String(required=True)
    aula_id = String(required=True)
    nota = Float(allow_none=True)


class AvaliacaoOut(Schema):
    id = String()
    aluno_id = String()
    aula_id = String()
    nota = Float(allow_none=True)
