from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from services.database import db
from models import Matricula, Aluno, Curso

matricula_bp = Blueprint("matriculas", __name__, url_prefix="/matriculas")


@matricula_bp.route("/", methods=["GET"])
def listar_matriculas():
    matriculas = Matricula.query.all()
    return jsonify(
        [
            {
                "id": m.id,
                "aluno_id": m.aluno_id,
                "curso_id": m.curso_id,
                "status": m.status,
            }
            for m in matriculas
        ]
    )


@matricula_bp.route("/<string:matricula_id>", methods=["GET"])
def obter_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    return jsonify(
        {
            "id": matricula.id,
            "aluno_id": matricula.aluno_id,
            "curso_id": matricula.curso_id,
            "status": matricula.status,
        }
    )


@matricula_bp.route("/", methods=["POST"])
def criar_matricula():
    dados = request.get_json()
    if not dados or "aluno_id" not in dados or "curso_id" not in dados:
        return jsonify({"erro": "aluno_id e curso_id são obrigatórios"}), 400

    aluno_id = dados["aluno_id"]
    curso_id = dados["curso_id"]

    if not Aluno.query.get(aluno_id):
        return jsonify({"erro": "aluno_id inválido"}), 400

    if not Curso.query.get(curso_id):
        return jsonify({"erro": "curso_id inválido"}), 400

    matricula = Matricula(aluno_id=aluno_id, curso_id=curso_id)
    db.session.add(matricula)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"erro": "Esse aluno já está matriculado nesse curso"}), 409

    return (
        jsonify(
            {
                "id": matricula.id,
                "aluno_id": matricula.aluno_id,
                "curso_id": matricula.curso_id,
                "status": matricula.status,
            }
        ),
        201,
    )

@matricula_bp.route("/<string:matricula_id>", methods=["PUT"])
def atualizar_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    dados = request.get_json() or {}
    matricula.status = dados.get("status", matricula.status)
    db.session.commit()
    return jsonify({"id": matricula.id, "status": matricula.status})


@matricula_bp.route("/<string:matricula_id>", methods=["DELETE"])
def deletar_matricula(matricula_id):
    matricula = Matricula.query.get_or_404(matricula_id)
    db.session.delete(matricula)
    db.session.commit()
    return "", 204
