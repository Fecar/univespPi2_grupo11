from apiflask import APIFlask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from services.database import db, migrate
from routes import register_routes
from services.admin import cria_primeiro_professor


def create_app(Config_object=Config):

    app = APIFlask(__name__)
    app.config.from_object(Config_object)

    CORS(app, origins=["http://localhost:5173"])

    db.init_app(app)
    migrate.init_app(app, db)
    JWTManager(app)

    import models

    register_routes(app)

    @app.cli.command("seed-admin")
    def seed_admin():
        cria_primeiro_professor()

    return app


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
