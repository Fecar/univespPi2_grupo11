from apiflask import APIFlask
from config import Config
from services.database import db, migrate
from routes import register_routes

def create_app():

    app = APIFlask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    migrate.init_app(app, db)

    import models
    register_routes(app)


    return app

app = create_app()


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
