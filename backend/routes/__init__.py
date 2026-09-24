from .professor_routes import professor_bp
from .aluno_routes import aluno_bp
from .curso_routes import curso_bp
from .matricula_routes import matricula_bp
from .auth_routes import auth_bp

#    NOTE: ADICIONAR TODAS AS ROTAS NESSE AQUIVO PARA IMPORTAR AUTOMÁTICAMENTE NO app.py

def register_routes(app):
    app.register_blueprint(professor_bp)
    app.register_blueprint(aluno_bp)
    app.register_blueprint(curso_bp)
    app.register_blueprint(matricula_bp)
    app.register_blueprint(auth_bp)
