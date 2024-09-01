# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from os import environ
import logging

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = environ.get('DATABASE_URL') or 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    published_year = db.Column(db.Integer, nullable=False)

    def __init__(self, title, author, published_year):
        self.title = title
        self.author = author
        self.published_year = published_year

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Book Service API"}), 200

@app.route('/books', methods=['GET'])
def get_books():
    try:
        books = Book.query.all()
        return jsonify([
            {"id": book.id, "title": book.title, "author": book.author, "published_year": book.published_year}
            for book in books
        ]), 200
    except Exception as e:
        logger.error(f"Error getting books: {str(e)}")
        return jsonify({"error": "An error occurred while fetching books"}), 500

@app.route('/books', methods=['POST'])
def add_book():
    try:
        data = request.json
        new_book = Book(title=data['title'], author=data['author'], published_year=data['published_year'])
        db.session.add(new_book)
        db.session.commit()
        logger.info(f"Book added: {new_book.title}")
        return jsonify({"message": "Book added successfully", "id": new_book.id}), 201
    except KeyError as e:
        logger.error(f"Missing key in request: {str(e)}")
        return jsonify({"error": f"Missing required field: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Error adding book: {str(e)}")
        return jsonify({"error": "An error occurred while adding the book"}), 500

@app.route('/books/<int:id>', methods=['GET'])
def get_book(id):
    try:
        book = Book.query.get_or_404(id)
        return jsonify({"id": book.id, "title": book.title, "author": book.author, "published_year": book.published_year}), 200
    except Exception as e:
        logger.error(f"Error getting book {id}: {str(e)}")
        return jsonify({"error": f"Book with id {id} not found"}), 404

@app.route('/books/<int:id>', methods=['PUT'])
def update_book(id):
    try:
        book = Book.query.get_or_404(id)
        data = request.json
        book.title = data.get('title', book.title)
        book.author = data.get('author', book.author)
        book.published_year = data.get('published_year', book.published_year)
        db.session.commit()
        logger.info(f"Book updated: {book.title}")
        return jsonify({"message": "Book updated successfully"}), 200
    except Exception as e:
        logger.error(f"Error updating book {id}: {str(e)}")
        return jsonify({"error": f"An error occurred while updating book {id}"}), 500

@app.route('/books/<int:id>', methods=['DELETE'])
def delete_book(id):
    try:
        book = Book.query.get_or_404(id)
        db.session.delete(book)
        db.session.commit()
        logger.info(f"Book deleted: {book.title}")
        return jsonify({"message": "Book deleted successfully"}), 200
    except Exception as e:
        logger.error(f"Error deleting book {id}: {str(e)}")
        return jsonify({"error": f"An error occurred while deleting book {id}"}), 500

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)