from apiflask import Schema
from apiflask.fields import String

class MatriculaIn(Schema):
    aluno_id = String(required=True)
    curso_id = String(required=True)

class MatriculaStatusIn(Schema):
    status = String(required=False)

class MatriculaOut(Schema):
    id = String()
    aluno_id = String()
    curso_id = String()
    status = String()
