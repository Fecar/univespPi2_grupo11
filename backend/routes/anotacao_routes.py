from apiflask import APIBlueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.database import db
from services.auth import admin_required
from models import Anotacao, Aluno
from schemas.anotacao import AnotacaoIn, AnotacaoOut

anotacao_bp = APIBlueprint("anotacoes", __name__, url_prefix="/anotacoes")


@anotacao_bp.route("/", methods=["GET"])
@jwt_required()
@anotacao_bp.output(AnotacaoOut(many=True))
def listar_anotacoes():
    return Anotacao.query.all()


@anotacao_bp.route("/<string:anotacao_id>", methods=["GET"])
@jwt_required()
@anotacao_bp.output(AnotacaoOut)
def obter_anotacao(anotacao_id):
    return Anotacao.query.get_or_404(anotacao_id)


@anotacao_bp.route("/", methods=["POST"])
@jwt_required()
@anotacao_bp.input(AnotacaoIn)
@anotacao_bp.output(AnotacaoOut, status_code=201)
def criar_anotacao(json_data):
    if not Aluno.query.get(json_data["aluno_id"]):
        abort(400, message="aluno_id inválido")

    anotacao = Anotacao(**json_data, professor_id=get_jwt_identity())
    db.session.add(anotacao)
    db.session.commit()
    return anotacao


@anotacao_bp.route("/<string:anotacao_id>", methods=["PUT"])
@jwt_required()
@anotacao_bp.input(AnotacaoIn(partial=True))
@anotacao_bp.output(AnotacaoOut)
def atualizar_anotacao(anotacao_id, json_data):
    anotacao = Anotacao.query.get_or_404(anotacao_id)
    for campo, valor in json_data.items():
        setattr(anotacao, campo, valor)
    db.session.commit()
    return anotacao


@anotacao_bp.route("/<string:anotacao_id>", methods=["DELETE"])
@admin_required
def deletar_anotacao(anotacao_id):
    anotacao = Anotacao.query.get_or_404(anotacao_id)
    db.session.delete(anotacao)
    db.session.commit()
    return "", 204
