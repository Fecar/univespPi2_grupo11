from .professor_routes import professor_bp

#    NOTE: ADICIONAR TODAS AS ROTAS NESSE AQUIVO PARA IMPORTAR AUTOMÁTICAMENTE NO app.py

def register_routes(app):
    app.register_blueprint(professor_bp)
