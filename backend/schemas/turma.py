from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length


class TurmaIn(Schema):
    nome = String(required=True, validate=Length(min=1, max=255))
    curso_id = String(required=True)
    professor_id = String(required=True)


class TurmaOut(Schema):
    id = String()
    nome = String()
    curso_id = String()
    professor_id = String()


class TurmaAlunoIn(Schema):
    aluno_id = String(required=True)
    turma_id = String(required=True)


class TurmaAlunoOut(Schema):
    id = String()
    aluno_id = String()
    turma_id = String()
