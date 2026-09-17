import uuid
from services.database import db
from datetime import datetime, timezone


class Matricula(db.Model):
    __tablename__= "matriculas"
    __table_args__ = (
        db.UniqueConstraint("aluno_id", "curso_id", name="uq_matricula_alunos_curso"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    aluno_id = db.Column(db.String(36), db.ForeignKey("alunos.id"), nullable=False)
    curso_id = db.Column(db.String(36), db.ForeignKey("curso.id"), nullable=False)

    aluno = db.relationship("Aluno", backref="matriculas")
    curso = db.relationship("Curso", backref="matriculas")

    data_matricula = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    status = db.Column(db.String(20), default="ativa", nullable=False)
