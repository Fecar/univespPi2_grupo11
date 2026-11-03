from werkzeug.security import generate_password_hash
from apiflask import APIBlueprint, abort
from services.database import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth import admin_required, self_or_admin_required
from models import Professor
from schemas.professor import ProfessorIn, ProfessorOut, ProfessorOutId

professor_bp = APIBlueprint("professores", __name__, url_prefix="/professores")


@professor_bp.route("/", methods=["GET"])
@self_or_admin_required
@professor_bp.output(ProfessorOut(many=True))
def listar_professores():
    return Professor.query.all()


@professor_bp.route("/<string:professor_id>", methods=["GET"])
@self_or_admin_required
@professor_bp.output(ProfessorOutId)
def obter_professor(professor_id):
    return db.get_or_404(Professor, professor_id)


@professor_bp.route("/", methods=["POST"])
@admin_required
@professor_bp.input(ProfessorIn)
@professor_bp.output(ProfessorOut, status_code=201)
def criar_professor(json_data):
    senha = json_data.pop("senha")
    professor = Professor(**json_data, senha_hash=generate_password_hash(senha))
    db.session.add(professor)
    db.session.commit()
    return professor


@professor_bp.route("/<string:professor_id>", methods=["PUT"])
@self_or_admin_required
@professor_bp.input(ProfessorIn(partial=True))
@professor_bp.output(ProfessorOutId)
def atualizar_professor(professor_id, json_data):
    if professor_id == get_jwt_identity() and "privilegio" in json_data:
        abort(400, message="Você não pode alterar seu próprio privilégio")
    professor = db.get_or_404(Professor, professor_id)
    if "senha" in json_data:
        professor.senha_hash = generate_password_hash(json_data.pop("senha"))
    for campo, valor in json_data.items():
        setattr(professor, campo, valor)
    db.session.commit()
    return professor


@professor_bp.route("/<string:professor_id>", methods=["DELETE"])
@admin_required
def deletar_professor(professor_id):
    if professor_id == get_jwt_identity():
        abort(400, message="Você não pode deletar sua própria conta")

    professor = db.get_or_404(Professor, professor_id)
    db.session.delete(professor)
    db.session.commit()
    return "", 204
