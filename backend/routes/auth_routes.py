from datetime import datetime, timedelta, timezone
from apiflask import APIBlueprint, abort
from flask_jwt_extended import create_access_token
from werkzeug.security import check_password_hash
from services.database import db
from models import Professor
from schemas.auth import LoginIn, LoginOut

auth_bp = APIBlueprint("auth", __name__, url_prefix="/auth")

MAX_TENTATIVAS = 5
TEMPO_BLOQUEIO = timedelta(minutes=15)


@auth_bp.route("/login", methods=["POST"])
@auth_bp.input(LoginIn)
@auth_bp.output(LoginOut)
def login(json_data):
    professor = Professor.query.filter_by(email=json_data["email"]).first()
    if not professor:
        abort(401, message="Credenciais inválidas")

    now = datetime.now(timezone.utc)
    bloqueado_ate = professor.bloqueado_ate

    if bloqueado_ate and bloqueado_ate.tzinfo is None:
        bloqueado_ate = bloqueado_ate.replace(tzinfo=timezone.utc)

    if bloqueado_ate and bloqueado_ate > now:
        abort(
            401, message="Conta temporariamente bloqueada, tente novamente mais tarde!"
        )

    if not check_password_hash(professor.senha_hash, json_data["senha"]):
        professor.tentativas_falhas += 1
        if professor.tentativas_falhas >= MAX_TENTATIVAS:
            professor.bloqueado_ate = now + TEMPO_BLOQUEIO
        db.session.commit()
        abort(401, message="Crendenciais inválidas")

    professor.tentativas_falhas = 0
    professor.bloqueado_ate = None
    db.session.commit()

    token = create_access_token(identity=professor.id)
    return {"access_token": token}
