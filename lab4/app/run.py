from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, create_app
from app.forms import CreateForm, LoginForm, PasswordForm, UpdateForm
from app.models import Users, Roles

app = create_app()


@app.errorhandler(404)
def page_not_found(e):
    if e.description[:3] == 'The':
        e.description = (
            "Запрашиваемый URL не найден на сервере. "
            "Если вы ввели URL самостоятельно, проверьте написание и попробуйте снова."
        )
    return render_template('404.html', cause=e.description, title='Страница не найдена'), 404


@app.route('/')
def index():
    return render_template('index.html', users=Users.query.all(), title='Лабораторная работа №4')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        user = Users.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user, remember)
            flash('Вы успешно вошли.', category='success')
            return redirect(url_for('index'))
        else:
            flash('Неправильное имя пользователя или пароль.', category='fail')

    return render_template('login.html', title='Авторизация', form=form)


@app.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm()
    form.role_id.choices = [(role.id, role.name) for role in Roles.query.all()]

    if form.validate_on_submit():
        user = Users(
            username=form.username.data,
            password_hash=generate_password_hash(form.password.data),
            role_id=form.role_id.data,
            last_name=form.last_name.data,
            first_name=form.first_name.data,
            patronymic=form.patronymic.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Пользователь успешно добавлен.', category='success')
        return redirect(url_for('index'))

    return render_template('create.html', title='Создание пользователя', form=form)


@app.route('/read/<int:id>')
def read(id):
    user = Users.query.get_or_404(id, description=f'Пользователь с {id=} не найден')
    return render_template('read.html', user=user, title='Просмотр данных пользователя')


@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    user = Users.query.get_or_404(id, description=f'Пользователь с {id=} не найден')

    form = UpdateForm(obj=user)
    form.role_id.choices = [(role.id, role.name) for role in Roles.query.all()]

    if form.validate_on_submit():
        user.role_id = form.role_id.data
        user.last_name = form.last_name.data
        user.first_name = form.first_name.data
        user.patronymic = form.patronymic.data
        db.session.commit()
        flash('Пользователь успешно отредактирован.', category='success')
        return redirect(url_for('index'))

    return render_template('update.html', form=form, title='Редактирование пользователя', id=id)


@app.route('/delete/<int:id>', methods=['POST'])
@login_required
def delete(id):
    user = Users.query.get_or_404(id, description=f'Пользователь с {id=} не найден')
    db.session.delete(user)
    db.session.commit()
    flash('Пользователь успешно удален.', category='success')
    return redirect(url_for('index'))


@app.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    form = PasswordForm()

    if form.validate_on_submit():
        current_user.password_hash = generate_password_hash(form.new_password.data)
        db.session.commit()
        flash('Пароль успешно обновлен.', category='success')
        return redirect(url_for('index'))

    return render_template('password.html', form=form, title='Смена пароля')


if __name__ == '__main__':
    app.run()
