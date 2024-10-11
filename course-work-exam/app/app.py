from flask import Flask, render_template, request
from sqlalchemy import func

from auth import bp as auth_bp, init_login_manager
from books import bp as books_bp
from config import ACCEPTED_STATUS_ID
from models import db, Book, Genre, Review, BookGenre, Cover
from reviews import bp as reviews_bp

app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

init_login_manager(app)

app.register_blueprint(auth_bp)
app.register_blueprint(books_bp)
app.register_blueprint(reviews_bp)


# Главная страница с пагинацией
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    books_query = (
        db.session.query(
            Book.id,
            Book.name,
            func.group_concat(Genre.name.distinct()).label('genres'),
            Book.year,
            func.round(func.avg(Review.grade), 1).label('avg_grade'),
            func.count(Review.id.distinct()).label('review_count'),
            Cover.filename,
            Cover.mime_type
        )
        .join(BookGenre, BookGenre.book_id == Book.id)
        .join(Genre, Genre.id == BookGenre.genre_id)
        .outerjoin(Review, (Review.book_id == Book.id) & (Review.status_id == ACCEPTED_STATUS_ID))
        .outerjoin(Cover, Cover.id == Book.cover_id)
        .group_by(Book.id, Book.name, Book.year, Cover.filename)
        .order_by(Book.year.desc())
    )
    pagination = books_query.paginate(per_page=9, page=page)
    books = pagination.items
    return render_template("index.html", books=books, pagination=pagination)


if __name__ == '__main__':
    app.run(debug=True)
