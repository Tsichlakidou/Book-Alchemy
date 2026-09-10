from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# id, name, birth_date, and date_of_death
class Author(db.Model):
    __tablename__ = "authors"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    date_of_death = db.Column(db.Date)

    def __repr__(self):
        return f"Author({self.name}, {self.birth_date}, {self.date_of_death})"

class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    isbn = db.Column(db.String(100),unique=True, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    author = db.relationship('Author')
    publication_year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"Book({self.title}, {self.author_id}, {self.publication_year})"

