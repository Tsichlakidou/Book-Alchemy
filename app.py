"""Flask application for managing books and authors."""

import os
from datetime import datetime

from flask import Flask, redirect, url_for,request,render_template, flash
from sqlalchemy import or_

from data_models import db, Author, Book

app = Flask(__name__)
app.secret_key = 'your-secret-key'

basedir = os.path.abspath(os.path.dirname(__file__))

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"sqlite:///{os.path.join(basedir, 'data/library.sqlite')}"
)


@app.route('/')
def home():
    """Display the library's books and handle search and sorting."""
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
    elif sort_by == "author":
        books = Book.query.join(Author).order_by(Author.name).all()
    else:
        books = Book.query.all()
    return render_template('home.html', books=books)


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """Display the author form and add a new author to the database."""
    success = False
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        birth_date_str = request.form.get('birth_date', '')
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        date_of_death_str = request.form.get('date_of_death')
        if date_of_death_str:
            date_of_death = datetime.strptime(date_of_death_str,'%Y-%m-%d').date()
        else:
            date_of_death = None
        existing_author = Author.query.filter(Author.name == name).first()
        if name and not existing_author:
            author = Author(name = name, birth_date = birth_date, date_of_death = date_of_death)
            db.session.add(author)
            db.session.commit()
            success = True
        elif existing_author:
            flash("Author name already exists!")
        else:
            flash("Author name cannot be empty!")
    return render_template('add_author.html', success = success)


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """Display the book form and add a new book to the database."""
    success = False
    if request.method == 'POST':
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        author_id_str = request.form.get('author_id')
        publication_year_str = request.form.get('publication_year')
        existing_book = Book.query.filter(Book.isbn == isbn).first()
        if author_id_str and publication_year_str and not existing_book:
            author_id = int(author_id_str)
            publication_year = int(publication_year_str)
            book = Book(
                title=title,
                isbn=isbn,
                author_id=author_id,
                publication_year=publication_year
            )
            db.session.add(book)
            db.session.commit()
            success = True
        elif existing_book:
            flash("A book with this ISBN already exists!")
    authors = Author.query.all()
    return render_template('add_book.html', authors = authors, success = success)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """Delete a book and its author if the author has no other books."""
    book = Book.query.filter(Book.id == book_id).first()
    if book:
        author = book.author
        db.session.delete(book)
        db.session.commit()

        have_other_books = Book.query.filter(Book.author_id == author.id).all()
        if not have_other_books:
            db.session.delete(author)
            db.session.commit()
        flash("Book deleted successfully!")
    return redirect(url_for('home'))


@app.route('/book/<int:book_id>')
def details(book_id):
    """Display the details of a specific book."""
    book = Book.query.filter(Book.id == book_id).first()
    return render_template('details.html', book = book)


@app.route('/author/<int:author_id>')
def author_details(author_id):
    """Display the details of a specific author and their books."""
    books = Book.query.filter(Book.author_id == author_id).all()
    author = Author.query.filter(Author.id == author_id).first()
    return render_template('author_details.html', books = books, author = author)


db.init_app(app)
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
