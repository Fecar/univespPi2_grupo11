from apiflask import APIBlueprint, abort
from services.database import db
from models import Curso, Professor
from schemas.curso import CursoIn, CursoOut

curso_bp = APIBlueprint("cursos", __name__, url_prefix="/cursos")


@curso_bp.route("/", methods=["GET"])
@curso_bp.output(CursoOut(many=True))
def listar_cursos():
    return Curso.query.all()


@curso_bp.route("/<string:curso_id>", methods=["GET"])
@curso_bp.output(CursoOut)
def obter_curso(curso_id):
    return Curso.query.get_or_404(curso_id)


@curso_bp.route("/", methods=["POST"])
@curso_bp.input(CursoIn)
@curso_bp.output(CursoOut, status_code=201)
def criar_curso(json_data):
    professor_id = json_data["professor_id"]
    if not Professor.query.get(professor_id):
        abort(400, message="professor_id inválido")

    curso = Curso(**json_data)
    db.session.add(curso)
    db.session.commit()
    return curso


@curso_bp.route("/<string:curso_id>", methods=["PUT"])
@curso_bp.input(CursoIn(partial=True))
@curso_bp.output(CursoOut)
def atualizar_curso(curso_id, json_data):
    curso = Curso.query.get_or_404(curso_id)

    if "professor_id" in json_data and not Professor.query.get(json_data["professor_id"]):
        abort(400, message="professor_id inválido")

    for campo, valor in json_data.items():
        setattr(curso, campo, valor)

    db.session.commit()
    return curso


@curso_bp.route("/<string:curso_id>", methods=["DELETE"])
def deletar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    db.session.delete(curso)
    db.session.commit()
    return "", 204
