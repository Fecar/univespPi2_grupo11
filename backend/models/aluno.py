import uuid
from services.database import db
from datetime import date, datetime, timezone


class Aluno(db.Model):
    __tablename__ = "alunos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)
    data_nascimento = db.Column(db.Date)
    responsavel = db.Column(db.String(255))
    numero_responsavel = db.Column(db.String(20))
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    numero_whatsapp = db.Column(db.String(20))

    # Controle
    data_cadastro = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    privilegio = db.Column(db.String(10))

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)

            if isinstance(val, (datetime, date)):
                data[column.name] = val.isoformat() if val else None
            else:
                data[column.name] = val

        return data
