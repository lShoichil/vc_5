from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile("config.py")
    db.init_app(app)

    from .models import Mems, User
    from .routes_mems import mem_routes
    from .routes_users import user_routes

    app.register_blueprint(mem_routes)
    app.register_blueprint(user_routes)

    return app
