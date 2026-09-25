import uuid
from services.database import db
from datetime import datetime, timezone


class Turma(db.Model):
    __tablename__ = "turmas"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)

    curso_id = db.Column(db.String(36), db.ForeignKey("cursos.id"), nullable=False)
    curso = db.relationship("Curso", backref="turmas")

    professor_id = db.Column(db.String(36), db.ForeignKey("professores.id"), nullable=False)
    professor = db.relationship("Professor", backref="turmas")

    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))


class TurmaAluno(db.Model):
    __tablename__ = "turma_alunos"
    __table_args__ = (
        db.UniqueConstraint("aluno_id", "turma_id", name="uq_turma_aluno"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aluno_id = db.Column(db.String(36), db.ForeignKey("alunos.id"), nullable=False)
    turma_id = db.Column(db.String(36), db.ForeignKey("turmas.id"), nullable=False)

    aluno = db.relationship("Aluno", backref="turmas")
    turma = db.relationship("Turma", backref="alunos")

    data_entrada = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
