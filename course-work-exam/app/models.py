from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


class Role(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)
    description = db.Column(db.Text, nullable=False)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    last_name = db.Column(db.String(32), nullable=False)
    first_name = db.Column(db.String(32), nullable=False)
    patronymic = db.Column(db.String(32))
    role_id = db.Column(db.ForeignKey('role.id', ondelete='CASCADE'), nullable=False)

    role = relationship('Role')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        return self.password_hash

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Cover(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String(128), nullable=False)
    mime_type = db.Column(db.String(32), nullable=False)
    md5_hash = db.Column(db.String(256), unique=True, nullable=False)


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    publisher = db.Column(db.String(128), nullable=False)
    author = db.Column(db.String(128), nullable=False)
    page_count = db.Column(db.Integer, nullable=False)
    cover_id = db.Column(db.ForeignKey('cover.id', ondelete='CASCADE'), nullable=False)


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False)


class BookGenre(db.Model):
    book_id = db.Column(db.ForeignKey('book.id', ondelete='CASCADE'), primary_key=True)
    genre_id = db.Column(db.ForeignKey('genre.id'), primary_key=True)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    grade = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    book_id = db.Column(db.ForeignKey('book.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    status_id = db.Column(db.ForeignKey('moderation_status.id'), nullable=False)

    user = relationship('User')
    book = relationship('Book')
    status = relationship('ModerationStatus', foreign_keys=[status_id])


class ModerationStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
