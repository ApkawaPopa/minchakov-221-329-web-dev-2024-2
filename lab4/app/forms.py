import re

from flask_login import current_user
from flask_wtf import FlaskForm
from werkzeug.security import check_password_hash
from wtforms.fields.choices import SelectField
from wtforms.fields.simple import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Length, EqualTo

from app.models import Users


def validate_username(form, username):
    data = username.data
    if not re.fullmatch(r'^[a-zA-Z\d]+$', data):
        raise ValidationError('Имя пользователя содержит недопустимый символ.')
    if Users.query.filter_by(username=data).first():
        raise ValidationError('Такое имя пользователя уже существует.')


def validate_password_constraints(form, password):
    data = password.data
    if not re.search(r'[a-zа-я]', data):
        raise ValidationError('В пароле должна быть хотя бы одна строчная буква.')
    if not re.search(r'[A-ZА-Я]', data):
        raise ValidationError('В пароле должна быть хотя бы одна заглавная буква.')
    if not re.search(r'\d', data):
        raise ValidationError('В пароле должна быть хотя бы одна цифра.')
    if not re.fullmatch(r'^[a-zA-Zа-яА-Я\d~!?@#$%^&*_\-+()\[\]{}></\\|"\'.,:;]+$', data):
        raise ValidationError('Пароль содержит недопустимый символ.')


def validate_old_password(form, old_password):
    data = old_password.data
    if not check_password_hash(current_user.password_hash, data):
        raise ValidationError('Пароль неверный.')


data_required = DataRequired('Поле не может быть пустым')


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[data_required])
    password = PasswordField('Пароль', validators=[data_required])
    remember = BooleanField('Запомнить меня', default=False)
    submit = SubmitField('Войти')


class CreateForm(FlaskForm):
    username = StringField(
        'Имя пользователя',
        validators=[
            data_required,
            Length(min=5, message='Длина имени пользователя должна быть не меньше пяти символов.'),
            validate_username
        ]
    )
    password = PasswordField(
        'Пароль',
        validators=[
            data_required,
            Length(min=8, max=128, message='Длина пароля должна быть от 8 до 128 символов.'),
            validate_password_constraints
        ]
    )
    last_name = StringField('Фамилия', validators=[data_required])
    first_name = StringField('Имя', validators=[data_required])
    patronymic = StringField('Отчество')
    role_id = SelectField('Роль', coerce=int)
    submit = SubmitField('Создать')


class UpdateForm(CreateForm):
    username = None
    password = None
    submit = SubmitField('Отредактировать')


class PasswordForm(FlaskForm):
    old_password = PasswordField('Старый пароль', validators=[data_required, validate_old_password])
    new_password = PasswordField(
        'Новый пароль',
        validators=[
            validate_password_constraints,
            data_required,
            Length(min=8, max=128, message='Длина пароля должна быть от 8 до 128 символов.'),
        ]
    )
    new_password_repeat = PasswordField(
        'Повторите новый пароль',
        validators=[data_required, EqualTo('new_password', message='Пароли не равны.')]
    )
    submit = SubmitField('Обновить')
