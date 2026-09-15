from flask import Blueprint, request, jsonify
from services.database import db
from models import Professor

professor_bp = Blueprint("professores", __name__, url_prefix="/professores")


@professor_bp.route("/", methods=["GET"])
def listar_professores():
    professores = Professor.query.all()
    return jsonify([
        {"id": p.id, "nome": p.nome, "email": p.email}
        for p in professores
    ])


@professor_bp.route("/<int:professor_id>", methods=["GET"])
def obter_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    return jsonify({"id": professor.id, "nome": professor.nome, "email": professor.email})


@professor_bp.route("/", methods=["POST"])
def criar_professor():
    dados = request.get_json()
    if not dados or "nome" not in dados or "email" not in dados:
        return jsonify({"erro": "nome e email são obrigatórios"}), 400

    professor = Professor(nome=dados["nome"], email=dados["email"])
    db.session.add(professor)
    db.session.commit()
    return jsonify({"id": professor.id, "nome": professor.nome, "email": professor.email}), 201


@professor_bp.route("/<int:professor_id>", methods=["PUT"])
def atualizar_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    dados = request.get_json() or {}

    professor.nome = dados.get("nome", professor.nome)
    professor.email = dados.get("email", professor.email)
    db.session.commit()
    return jsonify({"id": professor.id, "nome": professor.nome, "email": professor.email})


@professor_bp.route("/<int:professor_id>", methods=["DELETE"])
def deletar_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    db.session.delete(professor)
    db.session.commit()
    return "", 204
