import uuid
from services.database import db
from datetime import datetime, timezone


class Aula(db.Model):
    __tablename__ = "aulas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)
    assunto = db.Column(db.String(255))
    materia = db.Column(db.String(255))
    data_hora = db.Column(db.DateTime, nullable=False)

    turma_id = db.Column(db.String(36), db.ForeignKey("turmas.id"), nullable=False)
    turma = db.relationship("Turma", backref="aulas")

    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class Avaliacao(db.Model):
    __tablename__ = "avaliacoes"
    __table_args__ = (
        db.UniqueConstraint("aluno_id", "aula_id", name="uq_avaliacao_aluno_aula"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nota = db.Column(db.Float, nullable=True)

    aluno_id = db.Column(db.String(36), db.ForeignKey("alunos.id"), nullable=False)
    aluno = db.relationship("Aluno", backref="avaliacoes")

    aula_id = db.Column(db.String(36), db.ForeignKey("aulas.id"), nullable=False)
    aula = db.relationship("Aula", backref="avaliacoes")
