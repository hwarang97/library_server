from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
import os


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

class Books(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False, unique=True)
    author: Mapped[str] = mapped_column(nullable=False)
    rating: Mapped[float] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<Books id: {self.id}, title: {self.title}, author: {self.author}, rating: {self.rating}>"

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books_collection.db"
db.init_app(app)

# create db once
with app.app_context():
    if not os.path.exists("instance/books_collection.db"):
        db.create_all()

@app.route('/', methods=['GET'])
def home():
    with app.app_context():
        all_books = db.session.query(Books).all()
    return render_template("index.html", books=all_books)

@app.route("/update/<int:book_id>", methods=["POST"])
def update(book_id):
    new_rating = request.form["new_rating"]
    with app.app_context():
        # book = Books.query.filter_by(id=book_id).first()
        book = db.get_or_404(Books, book_id)
        book.rating = float(new_rating)
        db.session.add(book)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/delete/<int:book_id>", methods=["GET"])
def delete(book_id):
    with app.app_context():
        book_to_delete = db.get_or_404(Books, book_id)
        db.session.delete(book_to_delete)
        db.session.commit()
    return redirect(url_for('home'))

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/submit", methods=['POST'])
def submit():
    book = Books(title=request.form["book_name"], author=request.form["book_author"], rating=request.form["book_rating"])
    with app.app_context():
        db.session.add(book)
        db.session.commit()
    return redirect("/")

@app.route("/edit/<int:book_id>")
def edit(book_id):
    book_to_update = None
    with app.app_context():
        book_to_update = Books.query.filter_by(id=book_id).first()

    return render_template("edit.html", book=book_to_update)


if __name__ == "__main__":
    app.run(debug=True)

