from apiflask import APIBlueprint
from services.database import db
from models import Aluno
from schemas.aluno import AlunoIn, AlunoOut

aluno_bp = APIBlueprint("alunos", __name__, url_prefix="/alunos")


@aluno_bp.route("/", methods=["GET"])
@aluno_bp.output(AlunoOut(many=True))
def listar_alunos():
    return Aluno.query.all()


@aluno_bp.route("/<string:aluno_id>", methods=["GET"])
@aluno_bp.output(AlunoOut)
def obter_aluno(aluno_id):
    return Aluno.query.get_or_404(aluno_id)


@aluno_bp.route("/", methods=["POST"])
@aluno_bp.input(AlunoIn)
@aluno_bp.output(AlunoOut, status_code=201)
def criar_aluno(json_data):
    aluno = Aluno(**json_data)
    db.session.add(aluno)
    db.session.commit()
    return aluno


@aluno_bp.route("/<string:aluno_id>", methods=["PUT"])
@aluno_bp.input(AlunoIn(partial=True))
@aluno_bp.output(AlunoOut)
def atualizar_aluno(aluno_id, json_data):
    aluno = Aluno.query.get_or_404(aluno_id)
    for campo, valor in json_data.items():
        setattr(aluno, campo, valor)
    db.session.commit()
    return aluno


@aluno_bp.route("/<string:aluno_id>", methods=["DELETE"])
def deletar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    return "", 204
