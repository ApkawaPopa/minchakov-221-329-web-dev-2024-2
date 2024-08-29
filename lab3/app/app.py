import uuid

from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_login import login_user, UserMixin, login_required, LoginManager, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = str(uuid.uuid4())
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Авторизуйтесь для получения доступа к этой странице'
login_manager.login_message_category = 'info'

user = {
    'username': 'user',
    'password': 'qwerty',
    'id': '12345'
}


class User(UserMixin):
    def __init__(self, username, id):
        self.username = username
        self.id = id


@login_manager.user_loader
def load_user(user_id):
    return None if user_id != user['id'] else User(user['username'], user['id'])


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/counter')
def counter():
    if session.get('counter') is None:
        session['counter'] = 0
    session['counter'] += 1
    return render_template('counter.html', title='Счетчик посещений', counter=session['counter'])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == user['username'] and password == user['password']:
            login_user(User(username, user['id']), remember=request.form.get('remember') == 'on')
            flash('Вы успешно вошли.', category='success')
            return redirect(url_for('index'))
        else:
            flash('Неправильное имя пользователя или пароль.', category='fail')

    return render_template('login.html', title='Авторизация')


@app.route('/profile/<id>')
@login_required
def profile(id):
    if id != current_user.id:
        flash('У вас нет доступа к этой странице.', category='fail')
        return redirect(url_for('index'))
    return render_template('profile.html', title='Профиль')
