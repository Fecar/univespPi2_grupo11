from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length

class CursoIn(Schema):
    nome = String(required=True, validate=Length(min=1, max=255))
    nivel = String(required=True, validate=Length(min=1, max=255))

class CursoOut(Schema):
    id = String()
    nome = String()
    nivel = String()
