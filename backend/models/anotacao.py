import uuid
from services.database import db
from datetime import datetime, timezone


class Anotacao(db.Model):
    __tablename__ = "anotacoes"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conteudo = db.Column(db.Text, nullable=False)

    aluno_id = db.Column(db.String(36), db.ForeignKey("alunos.id"), nullable=False)
    aluno = db.relationship("Aluno", backref="anotacoes")

    professor_id = db.Column(db.String(36), db.ForeignKey("professores.id"), nullable=False)
    professor = db.relationship("Professor", backref="anotacoes")

    data_hora = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
