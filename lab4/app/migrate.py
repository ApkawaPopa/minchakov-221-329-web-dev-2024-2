from werkzeug.security import generate_password_hash

from app import db, create_app
from app.models import Users, Roles

with create_app().app_context():
    db.create_all()
    db.session.add(Roles(name='Администратор', description='Главный человек на сайте'))
    db.session.add(Roles(name='Пользователь', description='Обычный пользователь'))
    db.session.add(
        Users(
            username='user',
            password_hash=generate_password_hash('qwerty'),
            first_name='Аркадий', last_name='Минчаков',
            role_id=Roles.query.filter_by(name='Администратор').first().id
        )
    )
    db.session.commit()
