import bleach
import markdown
from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_required, current_user

from books import check_role, GRADE_MAPPING
from config import PROCESSING_STATUS_ID, DECLINED_STATUS_ID, ACCEPTED_STATUS_ID
from models import db, Review, Book

bp = Blueprint('reviews', __name__, url_prefix='/reviews')


@bp.route('/my')
@login_required
def my_reviews():
    reviews_query = db.session.query(Review).filter(Review.user_id == current_user.id)
    page = request.args.get('page', 1, type=int)
    pagination = reviews_query.paginate(per_page=5, page=page)
    reviews = pagination.items
    for review in reviews:
        review.text = markdown.markdown(review.text)

    return render_template('reviews/my_reviews.html', reviews=reviews, pagination=pagination,
                           grade_mapping=GRADE_MAPPING)


@bp.route('/moderate')
@login_required
@check_role(['moderator'])
def moderate():
    reviews_query = db.session.query(Review).filter(Review.status_id == PROCESSING_STATUS_ID).order_by(
        Review.created_at.desc())

    page = request.args.get('page', 1, type=int)
    pagination = reviews_query.paginate(per_page=5, page=page)
    reviews = pagination.items

    return render_template('reviews/moderation.html', pagination=pagination, reviews=reviews,
                           grade_mapping=GRADE_MAPPING)


@bp.route('/moderate/<int:review_id>')
@login_required
@check_role(['moderator'])
def moderate_review(review_id):
    review = db.session.query(Review).get_or_404(review_id)
    review.text = markdown.markdown(review.text)
    return render_template('reviews/moderate_review.html', review=review, grade_mapping=GRADE_MAPPING)


@bp.route('/accept/<int:review_id>', methods=['POST'])
@login_required
@check_role(['moderator'])
def accept(review_id):
    review = db.session.query(Review).get_or_404(review_id)
    review.status_id = ACCEPTED_STATUS_ID
    db.session.commit()
    return redirect(url_for('reviews.moderate'))


@bp.route('/decline/<int:review_id>', methods=['POST'])
@login_required
@check_role(['moderator'])
def decline(review_id):
    review = db.session.query(Review).get_or_404(review_id)
    review.status_id = DECLINED_STATUS_ID
    db.session.commit()
    return redirect(url_for('reviews.moderate'))


# Написать рецензию
@bp.route('/write_review/<int:book_id>', methods=['GET', 'POST'])
@login_required
def write_review(book_id):
    book = db.session.query(Book).get_or_404(book_id)
    existing_review = db.session.query(Review).filter_by(book_id=book_id, user_id=current_user.id).first()

    if existing_review:
        flash('Вы уже написали рецензию на эту книгу.', 'warning')
        return redirect(url_for('books.view_book', book_id=book_id))

    if request.method == 'POST':
        grade = request.form['grade']
        text = request.form['text']

        sanitized_text = bleach.clean(text)

        review = Review(grade=grade, text=sanitized_text, book_id=book_id, user_id=current_user.id,
                        status_id=PROCESSING_STATUS_ID)
        db.session.add(review)
        db.session.commit()

        flash('Рецензия успешно добавлена!', 'success')
        return redirect(url_for('books.view_book', book_id=book_id))

    return render_template('reviews/write_review.html', book=book, grade_mapping=GRADE_MAPPING)
