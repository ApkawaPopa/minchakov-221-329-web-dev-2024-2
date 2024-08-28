import re
import uuid

from flask import Flask, render_template, request, make_response, flash

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/parameters')
def parameters():
    return render_template('parameters.html', title='Параметры URL')


@app.route('/headers')
def headers():
    return render_template('headers.html', title='Заголовки запроса')


@app.route('/cookie')
def cookie():
    response = make_response(render_template('cookie.html', title='Cookie запроса'))
    if 'some_cookie' in request.cookies:
        response.delete_cookie('some_cookie')
    else:
        response.set_cookie('some_cookie', 'Hello World!')
    return response


@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html', title='Параметры формы')


@app.route('/phone', methods=['GET', 'POST'])
def phone():
    phone = None

    if request.method == 'POST':
        is_phone_correct = True
        phone = request.form['phone']

        if not re.fullmatch(r'[\d ()\-.+]+', phone):
            is_phone_correct = False
            flash('Недопустимый ввод. В номере телефона встречаются недопустимые символы.', category='invalid-feedback')

        digits = [c for c in phone if c.isdigit()]
        if not (len(digits) == 10 or (len(digits) == 11 and digits[0] in ['7', '8'])):
            is_phone_correct = False
            flash('Недопустимый ввод. Неверное количество цифр.', category='invalid-feedback')

        digits = ''.join(digits[-10:])
        if is_phone_correct:
            phone = f'8-{digits[:3]}-{digits[3:6]}-{digits[6:8]}-{digits[8:]}'
            flash("Формат телефонного номера соблюден.", category='valid-feedback')

    return render_template('phone.html', title='Проверка телефонного номера', phone=phone)
