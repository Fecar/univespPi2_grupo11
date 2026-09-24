from apiflask import Schema
from apiflask.fields import String

class LoginIn(Schema):
    email = String(required=True)
    senha = String(required=True, load_only=True)

class LoginOut(Schema):
    access_token = String()
