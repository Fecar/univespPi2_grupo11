from sqlalchemy import Boolean
from flask_login import UserMixin
from db import db 

class Usuario(UserMixin, db.Model):
    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha
    
    __tablename__ = 'usuarios_tb'
    id = db.Column(db.Integer, primary_key=True)
    is_active = db.Column(Boolean, default=True, nullable=False)
    is_admin = db.Column(Boolean, default=False, nullable=False)
    email = db.Column(db.String(30), unique=True)
    senha = db.Column(db.String(10))
    nome = db.Column(db.String(35))