import uuid
from services.database import db
from datetime import date, datetime, timezone


class Curso(db.Model):
    __tablename__ = "cursos"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.String(255), nullable=False)

    data_criacao = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        data = {}
        for column in self.__table__.columns:
            val = getattr(self, column.name)
            if isinstance(val, (datetime, date)):
                data[column.name] = val.isoformat() if val else None
            else:
                data[column.name] = val

        return data
