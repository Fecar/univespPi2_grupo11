from apiflask import Schema
from apiflask.fields import String
from apiflask.validators import Length

class CursoIn(Schema):
    nome = String(required=True, validate=Length(min=1, max=255))
    nivel = String(required=True, validate=Length(min=1, max=255))
    professor_id = String(required=True)

class CursoOut(Schema):
    id = String()
    nome = String()
    nivel = String()
    professor_id = String()
