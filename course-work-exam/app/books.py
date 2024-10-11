import hashlib
import os
from functools import wraps

import bleach
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask import current_app
from flask_login import current_user, login_required
from markdown import markdown
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from config import ACCEPTED_STATUS_ID
from models import db, Book, Genre, Review, BookGenre, Cover

bp = Blueprint('books', __name__, url_prefix='/books')

# Текстовое описание оценок
GRADE_MAPPING = ['ужасно', 'плохо', 'неудовлетворительно', 'удовлетворительно', 'хорошо', 'отлично']

# Допустимые расширения для изображения
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def allowed_file(filename):
    return '.' in filename and filename.split('.')[-1].lower() in ALLOWED_EXTENSIONS


# Декоратор для разграничения прав доступа, на вход подается список ролей, у которых есть разрешение
def check_role(roles):
    def decorator(func):
        @wraps(func)
        def decorated(*args, **kwargs):
            if current_user.role.name in roles:
                return func(*args, **kwargs)
            flash('У вас недостаточно прав для выполнения данного действия', 'danger')
            return redirect(url_for('index'))

        return decorated

    return decorator


# Сохранение обложки в таблицу cover
def save_cover_file(file):
    filename = secure_filename(file.filename)
    if not allowed_file(filename):
        raise ValueError("Недопустимый формат файла")

    file_data = file.read()
    md5_hash = hashlib.md5(file_data).hexdigest()
    mime_type = filename.rsplit('.', 1)[1].lower()

    # Запрос к базе данных, который проверяет, существует ли уже обложка с таким же хешем
    # Если существует, то мы используем уже имеющуюся обложку из базы данных
    existing_cover = db.session.query(Cover).filter_by(md5_hash=md5_hash).first()
    if existing_cover:
        return existing_cover.cover_id, None, None

    # Запрос к таблице covers, filename должно быть обязательно заполнено, поэтому присваиваем 
    # значение хэша. Здесь используется flush, он позволяет записывать данные в базу данных, 
    # но не фиксировать их, транзакция остается открытой до вызова commit. Это нужно чтобы получить
    # id обложки и записать filename 
    new_cover = Cover(md5_hash=md5_hash, mime_type=mime_type, filename=f'{md5_hash}')
    db.session.add(new_cover)
    db.session.flush()

    cover_id = new_cover.id
    new_cover.filename = f'{cover_id}'

    db.session.commit()

    file.seek(0)

    return cover_id, file_data, mime_type


# Добавление новой книги
@bp.route('/new_book', methods=['GET', 'POST'])
@login_required
@check_role(['administrator'])
def new_book():
    if request.method == 'POST':
        try:
            name = request.form['name']
            year = request.form['year']
            description = request.form['description']
            publisher = request.form['publisher']
            author = request.form['author']
            page_count = request.form['page_count']
            selected_genre_ids = request.form.getlist('genres')

            cover_file = request.files['cover']
            if cover_file and cover_file.filename != '':
                cover_id, cover_data, mime_type = save_cover_file(cover_file)
            else:
                cover_id = None

            description_html = bleach.clean(description)

            new_book = Book(
                name=name,
                year=year,
                description=description_html,
                publisher=publisher,
                author=author,
                page_count=page_count,
                cover_id=cover_id
            )
            db.session.add(new_book)
            db.session.commit()

            for genre_id in selected_genre_ids:
                connect = BookGenre(book_id=new_book.id, genre_id=int(genre_id))
                db.session.add(connect)

            db.session.commit()

            if cover_data:
                cover_path = os.path.join('static/images', f'{cover_id}.{mime_type}')
                cover_file.save(cover_path)

            flash('Книга успешно добавлена!', 'success')
            return redirect(url_for('books.view_book', book_id=new_book.id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')
        except ValueError as e:
            flash(str(e), 'danger')

    genres = db.session.query(Genre).all()
    return render_template('books/new_book.html', genres=genres)


# Редактирование книги
@bp.route('/edit_book/<int:book_id>', methods=['GET', 'POST'])
@login_required
@check_role(['administrator', 'moderator'])
def edit_book(book_id):
    book = db.session.query(Book).get_or_404(book_id)

    if request.method == 'POST':
        try:
            book.name = request.form['name']
            book.year = request.form['year']
            description = request.form['description']
            book.description = bleach.clean(description)
            book.publisher = request.form['publisher']
            book.author = request.form['author']
            book.page_count = request.form['page_count']

            selected_genre_ids = request.form.getlist('genres')
            db.session.query(BookGenre).filter(BookGenre.book_id == book_id).delete()
            for genre_id in selected_genre_ids:
                connect = BookGenre(book_id=book_id, genre_id=int(genre_id))
                db.session.add(connect)

            db.session.commit()
            flash('Книга успешно обновлена!', 'success')
            return redirect(url_for('books.view_book', book_id=book_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('При сохранении данных возникла ошибка. Проверьте корректность введённых данных.', 'danger')

    genres = db.session.query(Genre).all()
    book_genres = [book_genre.genre_id for book_genre in db.session.query(BookGenre).filter_by(book_id=book_id).all()]
    return render_template('books/edit_book.html', book=book, genres=genres, book_genres=book_genres)


# Страница просмотра
@bp.route('/view_book/<int:book_id>')
def view_book(book_id):
    book = db.session.query(Book).get_or_404(book_id)
    book.description = markdown(book.description)

    reviews = db.session.query(Review).filter_by(book_id=book_id, status_id=ACCEPTED_STATUS_ID).all()
    for review in reviews:
        review.text = markdown(review.text)

    user_review = db.session.query(Review).filter_by(book_id=book_id, user_id=current_user.get_id()).first()
    if user_review:
        user_review.text = markdown(user_review.text)

    genre_ids = db.session.query(BookGenre.genre_id).filter_by(book_id=book_id).all()
    genres = db.session.query(Genre.name).filter(Genre.id.in_([id[0] for id in genre_ids])).all()
    genres = ", ".join([genre.name for genre in genres])

    cover_data = db.session.query(Cover.filename, Cover.mime_type).filter_by(id=book.cover_id).first()

    return render_template('books/view_book.html', book=book, reviews=reviews, genres=genres, cover_data=cover_data,
                           user_review=user_review, grade_mapping=GRADE_MAPPING)


# Удаление книги
@bp.route('/<int:book_id>/delete_book', methods=['POST'])
@login_required
@check_role(['administrator', 'moderator'])
def delete_book(book_id):
    book = db.session.query(Book).get_or_404(book_id)
    cover_id = book.cover_id

    try:
        db.session.delete(book)
        db.session.commit()

        if cover_id:
            cover = db.session.query(Cover).get(book.cover_id)
            if cover and cover.filename:
                cover_path = os.path.join('static/images', f'{cover.filename}.{cover.mime_type}')
                if os.path.exists(cover_path):
                    os.remove(cover_path)
                db.session.delete(cover)
                print("path***", cover_path)
            db.session.commit()

        flash('Книга успешно удалена', 'success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('Ошибка при удалении книги', 'danger')
        current_app.logger.error(f'Error deleting book: {str(e)}')
    except ValueError as e:
        flash(str(e), 'danger')

    return redirect(url_for('index'))
