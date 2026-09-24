from apiflask import APIBlueprint, abort
from sqlalchemy.exc import IntegrityError
from services.database import db
from models import Matricula, Aluno, Curso
from schemas.matricula import MatriculaIn, MatriculaStatusIn, MatriculaOut
from flask_jwt_extended import jwt_required
from services.auth import admin_required

matricula_bp = APIBlueprint("matriculas", __name__, url_prefix="/matriculas")


@matricula_bp.route("/", methods=["GET"])
@jwt_required()
@matricula_bp.output(MatriculaOut(many=True))
def listar_matriculas():
    return Matricula.query.all()


@matricula_bp.route("/<string:matricula_id>", methods=["GET"])
@admin_required
@matricula_bp.output(MatriculaOut)
def obter_matricula(matricula_id):
    return Matricula.query.get_or_404(matricula_id)


@matricula_bp.route("/", methods=["POST"])
@admin_required
@matricula_bp.input(MatriculaIn)
@matricula_bp.output(MatriculaOut, status_code=201)
def criar_matricula(json_data):
    aluno_id = json_data["aluno_id"]
    curso_id = json_data["curso_id"]

    if not Aluno.query.get(aluno_id):
        abort(400, message="aluno_id inválido")
    if not Curso.query.get(curso_id):
        abort(400, message="curso_id inválido")

    matricula = Matricula(aluno_id=aluno_id, curso_id=curso_id)
    db.session.add(matricula)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, message="Esse aluno já está matriculado nesse curso")

    return matricula


@matricula_bp.route("/<string:matricula_id>", methods=["PUT"])
@admin_required
@matricula_bp.input(MatriculaStatusIn)
@matricula_bp.output(MatriculaOut)
def atualizar_matricula(matricula_id, json_data):
    matricula = Matricula.query.get_or_404(matricula_id)
    if "status" in json_data:
        matricula.status = json_data["status"]
    db.session.commit()
    return matricula


@matricula_bp.route("/<string:matricula_id>", methods=["DELETE"])
@admin_required
def deletar_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    db.session.delete(matricula)
    db.session.commit()
    return "", 204
