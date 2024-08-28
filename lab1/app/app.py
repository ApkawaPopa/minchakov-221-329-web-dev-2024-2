import random
import uuid

from flask import Flask, render_template, request, redirect, flash, url_for
from faker import Faker

fake = Faker()

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

images_ids = ['7d4e9175-95ea-4c5f-8be5-92a6b708bb3c',
              '2d2ab7df-cdbc-48a8-a936-35bba702def5',
              '6e12f3de-d5fd-4ebb-855b-8cbc485278b7',
              'afc2cfe7-5cac-4b80-9b9a-d5c65ef0c728',
              'cab5b7f2-774e-4884-a200-0c0180fa777f']


def generate_comments(replies=True):
    comments = []
    for i in range(random.randint(1, 3)):
        comment = {'author': fake.name(), 'text': fake.text()}
        if replies:
            comment['replies'] = generate_comments(replies=False)
        comments.append(comment)
    return comments


def generate_post(i):
    return {
        'title': 'Заголовок поста',
        'text': fake.paragraph(nb_sentences=100),
        'author': fake.name(),
        'date': fake.date_time_between(start_date='-2y', end_date='now'),
        'image_id': f'{images_ids[i]}.jpg',
        'comments': generate_comments()
    }


posts_list = sorted([generate_post(i) for i in range(5)], key=lambda p: p['date'], reverse=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/posts')
def posts():
    return render_template('posts.html', title='Посты', posts=posts_list)


@app.route('/posts/<int:index>')
def post(index):
    p = posts_list[index]
    return render_template('post.html', title=p['title'], post=p)


@app.route('/post_comment/<string:post_image_id>', methods=['POST'])
def post_comment(post_image_id):
    pos = -1
    for i in range(len(posts_list)):
        if posts_list[i]['image_id'] == post_image_id:
            pos = i
            break
    if pos == -1:
        return "Пост не найден", 404

    author = request.form['author']
    text = request.form['text']

    if not author or not text:
        flash('Все поля обязательны для заполнения')
        return redirect(url_for('post', index=pos))

    comment = {
        'author': author,
        'text': text
    }
    posts_list[pos]['comments'].append(comment)
    flash('Комментарий успешно добавлен!')
    return redirect(url_for('post', index=pos))


@app.route('/about')
def about():
    return render_template('about.html', title='Об авторе')
