from apiflask import APIBlueprint, abort
from services.database import db
from models import Curso
from schemas.curso import CursoIn, CursoOut
from flask_jwt_extended import jwt_required
from services.auth import admin_required

curso_bp = APIBlueprint("cursos", __name__, url_prefix="/cursos")


@curso_bp.route("/", methods=["GET"])
@jwt_required()
@curso_bp.output(CursoOut(many=True))
def listar_cursos():
    return Curso.query.all()


@curso_bp.route("/<string:curso_id>", methods=["GET"])
@jwt_required
@curso_bp.output(CursoOut)
def obter_curso(curso_id):
    return Curso.query.get_or_404(curso_id)


@curso_bp.route("/", methods=["POST"])
@admin_required
@curso_bp.input(CursoIn)
@curso_bp.output(CursoOut, status_code=201)
def criar_curso(json_data):
    curso = Curso(**json_data)
    db.session.add(curso)
    db.session.commit()
    return curso


@curso_bp.route("/<string:curso_id>", methods=["PUT"])
@admin_required
@curso_bp.input(CursoIn(partial=True))
@curso_bp.output(CursoOut)
def atualizar_curso(curso_id, json_data):
    curso = Curso.query.get_or_404(curso_id)

    for campo, valor in json_data.items():
        setattr(curso, campo, valor)

    db.session.commit()
    return curso


@curso_bp.route("/<string:curso_id>", methods=["DELETE"])
@admin_required
def deletar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    db.session.delete(curso)
    db.session.commit()
    return "", 204
