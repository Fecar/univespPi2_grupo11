import uuid
from services.database import db
from datetime import datetime, timezone


class Professor(db.Model):
    __tablename__= "professores"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    celular_whatsapp = db.Column(db.String(20))

    cep = db.Column(db.String(10))
    logradouro = db.Column(db.String(255))
    bairro = db.Column(db.String(100))
    cidade_uf = db.Column(db.String(100))

    graduacao_curso = db.Column(db.String(255))
    instituicao_ensino = db.Column(db.String(255))
    ano_conclusao = db.Column(db.Integer)
    pos_graduacao = db.Column(db.String(255))

    # Controle
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    privilegio = db.Column(db.String(10), default="comum")

    senha_hash = db.Column(db.String(255), nullable=False)
    tentativas_falhas = db.Column(db.Integer, default=0, nullable=False)
    bloqueado_ate = db.Column(db.DateTime, nullable=True)

