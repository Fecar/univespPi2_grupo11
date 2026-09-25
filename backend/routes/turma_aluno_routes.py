from apiflask import APIBlueprint, abort
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from services.database import db
from services.auth import admin_required
from models import TurmaAluno, Aluno, Turma
from schemas.turma import TurmaAlunoIn, TurmaAlunoOut

turma_aluno_bp = APIBlueprint("turma_alunos", __name__, url_prefix="/turma-alunos")


@turma_aluno_bp.route("/", methods=["GET"])
@jwt_required()
@turma_aluno_bp.output(TurmaAlunoOut(many=True))
def listar_turma_alunos():
    return TurmaAluno.query.all()


@turma_aluno_bp.route("/<string:turma_aluno_id>", methods=["GET"])
@jwt_required()
@turma_aluno_bp.output(TurmaAlunoOut)
def obter_turma_aluno(turma_aluno_id):
    return TurmaAluno.query.get_or_404(turma_aluno_id)


@turma_aluno_bp.route("/", methods=["POST"])
@admin_required
@turma_aluno_bp.input(TurmaAlunoIn)
@turma_aluno_bp.output(TurmaAlunoOut, status_code=201)
def criar_turma_aluno(json_data):
    aluno_id = json_data["aluno_id"]
    turma_id = json_data["turma_id"]

    if not Aluno.query.get(aluno_id):
        abort(400, message="aluno_id inválido")
    if not Turma.query.get(turma_id):
        abort(400, message="turma_id inválido")

    turma_aluno = TurmaAluno(aluno_id=aluno_id, turma_id=turma_id)
    db.session.add(turma_aluno)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, message="Esse aluno já está nessa turma")

    return turma_aluno


@turma_aluno_bp.route("/<string:turma_aluno_id>", methods=["DELETE"])
@admin_required
def deletar_turma_aluno(turma_aluno_id):
    turma_aluno = TurmaAluno.query.get_or_404(turma_aluno_id)
    db.session.delete(turma_aluno)
    db.session.commit()
    return "", 204
