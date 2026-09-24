import os

from models import Professor
from services.database import db
from werkzeug.security import generate_password_hash


def cria_primeiro_professor():
    password = os.getenv("ADMIN_PASS")
    email = os.getenv("ADMIN_USER")
    professor = Professor.query.filter_by(email=email).first()

    if not professor:
        print(f"Creating a default administrator email: {email}")
        passwd_encryp = generate_password_hash(password)
        admin = Professor(
            nome="Administardor",
            email=email,
            cpf="000.000.000-00",
            senha_hash=passwd_encryp,
            privilegio="admin",
        )
        db.session.add(admin)
        db.session.commit()

