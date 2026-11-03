import pytest
from werkzeug.security import generate_password_hash
from app import create_app
from config import TestConfig
from services.database import db
from models import Professor


@pytest.fixture
def app():
    app = create_app(TestConfig)

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def _criar_professor(privilegio, email, cpf):
    professor = Professor(
        nome="Professor Teste",
        email=email,
        cpf=cpf,
        senha_hash=generate_password_hash("senha1234"),
        privilegio=privilegio,
    )
    db.session.add(professor)
    db.session.commit()
    return professor


@pytest.fixture
def admin(app):
    return _criar_professor("admin", "admin@teste.com", cpf="000.000.001-00")


@pytest.fixture
def comum(app):
    return _criar_professor("comum", "comum@teste.com", cpf="000.000.002-00")


def _token(client, email):
    resposta = client.post("/auth/login", json={"email": email, "senha": "senha1234"})
    return resposta.get_json()["access_token"]


@pytest.fixture
def admin_headers(client, admin):
    return {"Authorization": f"Bearer {_token(client, admin.email)}"}


@pytest.fixture
def comum_headers(client, comum):
    return {"Authorization": f"Bearer {_token(client, comum.email)}"}
