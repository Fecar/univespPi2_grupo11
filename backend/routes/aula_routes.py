from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required
from services.database import db
from services.auth import admin_required
from models import Aula, Turma
from schemas.aula import AulaIn, AulaOut

aula_bp = APIBlueprint("aulas", __name__, url_prefix="/aulas")


@aula_bp.route("/", methods=["GET"])
@jwt_required()
@aula_bp.output(AulaOut(many=True))
def listar_aulas():
    return Aula.query.all()


@aula_bp.route("/<string:aula_id>", methods=["GET"])
@jwt_required()
@aula_bp.output(AulaOut)
def obter_aula(aula_id):
    return Aula.query.get_or_404(aula_id)


@aula_bp.route("/", methods=["POST"])
@admin_required
@aula_bp.input(AulaIn)
@aula_bp.output(AulaOut, status_code=201)
def criar_aula(json_data):
    if not Turma.query.get(json_data["turma_id"]):
        abort(400, message="turma_id inválido")

    aula = Aula(**json_data)
    db.session.add(aula)
    db.session.commit()
    return aula


@aula_bp.route("/<string:aula_id>", methods=["PUT"])
@jwt_required()
@aula_bp.input(AulaIn(partial=True))
@aula_bp.output(AulaOut)
def atualizar_aula(aula_id, json_data):
    aula = Aula.query.get_or_404(aula_id)

    if "turma_id" in json_data and not Turma.query.get(json_data["turma_id"]):
        abort(400, message="turma_id inválido")

    for campo, valor in json_data.items():
        setattr(aula, campo, valor)

    db.session.commit()
    return aula


@aula_bp.route("/<string:aula_id>", methods=["DELETE"])
@admin_required
def deletar_aula(aula_id):
    aula = Aula.query.get_or_404(aula_id)
    db.session.delete(aula)
    db.session.commit()
    return "", 204
