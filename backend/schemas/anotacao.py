from apiflask import Schema
from apiflask.fields import String, DateTime


class AnotacaoIn(Schema):
    aluno_id = String(required=True)
    conteudo = String(required=True)


class AnotacaoOut(Schema):
    id = String()
    aluno_id = String()
    professor_id = String()
    conteudo = String()
    data_hora = DateTime()
