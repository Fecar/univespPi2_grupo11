import uuid
from services.database import db
from datetime import datetime, timezone

class Curso(db.Model):
    __tablename__="cursos"


    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(255), nullable=False)

    professor_id = db.Column(db.String(36), db.ForeignKey("professores.id"), nullable=False)
    professor = db.relationship("Professor", backref="cursos")
    
    data_criacao = db.Column(db.Datetime, default=lambda: datetime.now(timezone.utc))
