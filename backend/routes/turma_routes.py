from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required
from services.database import db
from services.auth import admin_required
from models import Turma, Curso, Professor
from schemas.turma import TurmaIn, TurmaOut

turma_bp = APIBlueprint("turmas", __name__, url_prefix="/turmas")


@turma_bp.route("/", methods=["GET"])
@jwt_required()
@turma_bp.output(TurmaOut(many=True))
def listar_turmas():
    return Turma.query.all()


@turma_bp.route("/<string:turma_id>", methods=["GET"])
@jwt_required()
@turma_bp.output(TurmaOut)
def obter_turma(turma_id):
    return Turma.query.get_or_404(turma_id)


@turma_bp.route("/", methods=["POST"])
@admin_required
@turma_bp.input(TurmaIn)
@turma_bp.output(TurmaOut, status_code=201)
def criar_turma(json_data):
    if not Curso.query.get(json_data["curso_id"]):
        abort(400, message="curso_id inválido")
    if not Professor.query.get(json_data["professor_id"]):
        abort(400, message="professor_id inválido")

    turma = Turma(**json_data)
    db.session.add(turma)
    db.session.commit()
    return turma


@turma_bp.route("/<string:turma_id>", methods=["PUT"])
@jwt_required()
@turma_bp.input(TurmaIn(partial=True))
@turma_bp.output(TurmaOut)
def atualizar_turma(turma_id, json_data):
    turma = Turma.query.get_or_404(turma_id)

    if "curso_id" in json_data and not Curso.query.get(json_data["curso_id"]):
        abort(400, message="curso_id inválido")
    if "professor_id" in json_data and not Professor.query.get(json_data["professor_id"]):
        abort(400, message="professor_id inválido")

    for campo, valor in json_data.items():
        setattr(turma, campo, valor)

    db.session.commit()
    return turma


@turma_bp.route("/<string:turma_id>", methods=["DELETE"])
@admin_required
def deletar_turma(turma_id):
    turma = Turma.query.get_or_404(turma_id)
    db.session.delete(turma)
    db.session.commit()
    return "", 204
