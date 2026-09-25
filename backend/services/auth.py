from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from apiflask import abort
from services.database import db
from models import Professor


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        professor = db.session.get(Professor, get_jwt_identity())
        if not professor or professor.privilegio != "admin":
            abort(403, message="Acesso restrito a administradores")
        return fn(*args, **kwargs)
    return wrapper

def self_or_admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        professor = db.session.get(Professor, get_jwt_identity())
        if not professor:
            abort(401, message="Credenciais inválidas")
        if professor.id != kwargs.get("professor_id") and professor.privilegio != "admin":
            abort(403, message="Acesso restrito ao próprio perfil ou a administradores")
        return fn(*args, **kwargs)
    return wrapper
