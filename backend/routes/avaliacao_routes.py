from apiflask import APIBlueprint, abort
from sqlalchemy.exc import IntegrityError
from flask_jwt_extended import jwt_required
from services.database import db
from services.auth import admin_required
from models import Avaliacao, Aluno, Aula
from schemas.aula import AvaliacaoIn, AvaliacaoOut

avaliacao_bp = APIBlueprint("avaliacoes", __name__, url_prefix="/avaliacoes")


@avaliacao_bp.route("/", methods=["GET"])
@jwt_required()
@avaliacao_bp.output(AvaliacaoOut(many=True))
def listar_avaliacoes():
    return Avaliacao.query.all()


@avaliacao_bp.route("/<string:avaliacao_id>", methods=["GET"])
@jwt_required()
@avaliacao_bp.output(AvaliacaoOut)
def obter_avaliacao(avaliacao_id):
    return db.get_or_404(Avaliacao, avaliacao_id)


@avaliacao_bp.route("/", methods=["POST"])
@jwt_required()
@avaliacao_bp.input(AvaliacaoIn)
@avaliacao_bp.output(AvaliacaoOut, status_code=201)
def criar_avaliacao(json_data):
    if not db.session.get(Aluno, json_data["aluno_id"]):
        abort(400, message="aluno_id inválido")
    if not db.session.get(Aula, json_data["aula_id"]):
        abort(400, message="aula_id inválido")

    avaliacao = Avaliacao(**json_data)
    db.session.add(avaliacao)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        abort(409, message="Esse aluno já tem avaliação lançada nessa aula")

    return avaliacao


@avaliacao_bp.route("/<string:avaliacao_id>", methods=["PUT"])
@jwt_required()
@avaliacao_bp.input(AvaliacaoIn(partial=True))
@avaliacao_bp.output(AvaliacaoOut)
def atualizar_avaliacao(avaliacao_id, json_data):
    avaliacao = db.get_or_404(Avaliacao, avaliacao_id)
    for campo, valor in json_data.items():
        setattr(avaliacao, campo, valor)
    db.session.commit()
    return avaliacao


@avaliacao_bp.route("/<string:avaliacao_id>", methods=["DELETE"])
@admin_required
def deletar_avaliacao(avaliacao_id):
    avaliacao = db.get_or_404(Avaliacao, avaliacao_id)
    db.session.delete(avaliacao)
    db.session.commit()
    return "", 204
