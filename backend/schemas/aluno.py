from apiflask import Schema
from apiflask.fields import String

class AlunoIn(Schema):
    nome = String(required=True)
    email = String(required=True)
    cpf = String(required=True)

class AlunoOut(Schema):
    id = String()
    nome = String()
    email = String()
    cpf = String()
