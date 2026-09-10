from asyncio.windows_events import NULL

from flask import Flask, request,render_template
import os
from flask import Flask
from data_models import db, Author, Book
from datetime import datetime
from sqlalchemy import or_
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)

@app.route('/')
def home():
    search = request.args.get('search')
    if search:
        books = Book.query.join(Author).filter(or_
            (Book.title.ilike(f'%{search}%'),
     Book.isbn.ilike(f'%{search}%'),
             Author.name.ilike(f'%{search}'))).all()
        return render_template('home.html', books=books, search = search)

    sort_by = request.args.get('sort_by')
    if sort_by == 'title':
        books = Book.query.order_by(Book.title).all()
    elif sort_by == 'publication_year':
        books = Book.query.order_by(Book.publication_year).all()
    elif sort_by == 'author':
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.all()
    return render_template('home.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    success = False
    if request.method == 'POST':
        name = request.form.get('name')
        birth_date = datetime.strptime(request.form.get('birth_date'),'%Y-%m-%d').date()
        date_of_death_str = request.form.get('date_of_death')
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str,'%Y-%m-%d').date()
        else:
            date_of_death = None
        author = Author(name = name, birth_date = birth_date, date_of_death = date_of_death)
        db.session.add(author)
        db.session.commit()
        success = True
    return render_template('add_author.html', success = success)

@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    success = False
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        author_id = int(request.form.get('author_id'))
        publication_year = int(request.form.get('publication_year'))
        book = Book(title = title, isbn = isbn, author_id = author_id, publication_year = publication_year)
        db.session.add(book)
        db.session.commit()
        success = True
    authors = Author.query.all()
    return render_template('add_book.html', authors = authors, success = success)

db.init_app(app)
with app.app_context():
  db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
