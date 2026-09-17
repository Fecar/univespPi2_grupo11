from flask import Blueprint, request, jsonify
from services.database import db
from models import Curso, Professor

curso_bp = Blueprint("cursos", __name__, url_prefix="/cursos")


@curso_bp.route("/", methods=["GET"])
def listar_cursos():
    cursos = Curso.query.all()
    return jsonify([
        {
            "id": c.id,
            "nome": c.nome,
            "nivel": c.nivel,
            "professor_id": c.professor_id,
        }
        for c in cursos
    ])


@curso_bp.route("/<string:curso_id>", methods=["GET"])
def obter_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    return jsonify({
        "id": curso.id,
        "nome": curso.nome,
        "nivel": curso.nivel,
        "professor_id": curso.professor_id,
    })


@curso_bp.route("/", methods=["POST"])
def criar_curso():
    dados = request.get_json()
    if not dados or "nome" not in dados:
        return jsonify({"erro": "nome é obrigatório"}), 400

    professor_id = dados.get("professor_id")
    if professor_id and not Professor.query.get(professor_id):
        return jsonify({"erro": "ID do Professor é inválido"}), 400

    curso = Curso(
        nome=dados["nome"],
        nivel=dados.get("nivel"),
        professor_id=professor_id,
    )
    db.session.add(curso)
    db.session.commit()
    return jsonify({"id": curso.id, "nome": curso.nome, "professor_id": curso.professor_id}), 201


@curso_bp.route("/<string:curso_id>", methods=["PUT"])
def atualizar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    dados = request.get_json() or {}

    if "professor_id" in dados:
        professor_id = dados["professor_id"]
        if professor_id and not Professor.query.get(professor_id):
            return jsonify({"erro": "professor_id inválido"}), 400
        curso.professor_id = professor_id

    curso.nome = dados.get("nome", curso.nome)
    curso.nivel = dados.get("nivel", curso.nivel)
    db.session.commit()
    return jsonify({"id": curso.id, "nome": curso.nome, "professor_id": curso.professor_id})


@curso_bp.route("/<string:curso_id>", methods=["DELETE"])
def deletar_curso(curso_id):
    curso = Curso.query.get_or_404(curso_id)
    db.session.delete(curso)
    db.session.commit()
    return "", 204
