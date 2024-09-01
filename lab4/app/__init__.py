from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')

    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'login'
    login_manager.login_message = 'Авторизуйтесь для получения доступа к этой странице'
    login_manager.login_message_category = 'info'
    from app.models import Users
    @login_manager.user_loader
    def load_user(id):
        return Users.query.get(int(id))

    return app
