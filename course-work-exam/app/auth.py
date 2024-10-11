from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required

from models import db, User

user = User()

bp = Blueprint('auth', __name__, url_prefix='/auth')


def init_login_manager(app):
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Для выполнения данного действия необходимо пройти процедуру аутентификации'
    login_manager.login_message_category = 'warning'
    login_manager.user_loader(load_user)
    login_manager.init_app(app)


def load_user(user_id):
    user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one()
    return user


# Аутентификация
@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if login and password:
            user = db.session.execute(db.select(User).filter_by(username=username)).scalar_one_or_none()
            if user and user.check_password(password):
                login_user(user)
                flash('Вы успешно аутентифицированы.', 'success')
                next = request.args.get('next')
                return redirect(next or url_for('index'))
            else:
                flash('Невозможно аутентифицироваться с указанными логином и паролем', 'danger')
        else:
            flash('Заполните все поля', 'danger')
    return render_template('login.html')


# Выход из аккаунта
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))
