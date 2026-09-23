from apiflask import APIBlueprint
from services.database import db
from models import Professor
from schemas.professor import ProfessorIn, ProfessorOut, ProfessorOutId

professor_bp = APIBlueprint("professores", __name__, url_prefix="/professores")


@professor_bp.route("/", methods=["GET"])
@professor_bp.output(ProfessorOut(many=True))
def listar_professores():
    return Professor.query.all()


@professor_bp.route("/<string:professor_id>", methods=["GET"])
@professor_bp.output(ProfessorOutId)
def obter_professor(professor_id):
    return Professor.query.get_or_404(professor_id)


@professor_bp.route("/", methods=["POST"])
@professor_bp.input(ProfessorIn)
@professor_bp.output(ProfessorOut, status_code=201)
def criar_professor(json_data):
    professor = Professor(**json_data)
    db.session.add(professor)
    db.session.commit()
    return professor

@professor_bp.route("/<string:professor_id>", methods=["PUT"])
@professor_bp.input(ProfessorIn(partial=True))
@professor_bp.output(ProfessorOut)
def atualizar_professor(professor_id, json_data):
    professor = Professor.query.get_or_404(professor_id)
    for campo, valor in json_data.items():
        setattr(professor, campo, valor)
    db.session.commit()
    return professor


@professor_bp.route("/<string:professor_id>", methods=["DELETE"])
def deletar_professor(professor_id):
    professor = Professor.query.get_or_404(professor_id)
    db.session.delete(professor)
    db.session.commit()
    return "", 204
