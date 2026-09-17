from flask import Blueprint, request, jsonify
from services.database import db
from models import Aluno

aluno_bp = Blueprint("alunos", __name__, url_prefix="/alunos")


@aluno_bp.route("/", methods=["GET"])
def listar_alunos():
    alunos = Aluno.query.all()
    return jsonify([aluno.to_dict() for aluno in alunos]), 200


@aluno_bp.route("/<string:aluno_id>", methods=["GET"])
def obter_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    return (
        jsonify(
            {"id": aluno.id, "nome": aluno.nome, "email": aluno.email, "cpf": aluno.cpf}
        ),
        200,
    )


@aluno_bp.route("/", methods=["POST"])
def criar_aluno():
    dados = request.get_json()
    if not dados or "nome" not in dados or "email" not in dados or "cpf" not in dados:
        return jsonify({"erro": "nome, email e cpf são obrigatórios"}), 400

    aluno = Aluno(nome=dados["nome"], email=dados["email"], cpf=dados["cpf"])
    db.session.add(aluno)
    db.session.commit()
    return jsonify({"id": aluno.id, "nome": aluno.nome, "email": aluno.email}), 201


@aluno_bp.route("/<string:aluno_id>", methods=["PUT"])
def atualizar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    dados = request.get_json() or {}

    aluno.nome = dados.get("nome", aluno.nome)
    aluno.email = dados.get("email", aluno.email)
    db.session.commit()
    return jsonify({"id": aluno.id, "nome": aluno.nome, "email": aluno.email})


@aluno_bp.route("/<string:aluno_id>", methods=["DELETE"])
def deletar_aluno(aluno_id):
    aluno = Aluno.query.get_or_404(aluno_id)
    db.session.delete(aluno)
    db.session.commit()
    return "", 204
