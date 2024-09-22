from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import hashlib
import secrets
import re
import csv
import pandas as pd

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
# Load the original books dataset
books = pd.read_csv('books_data.csv')

# Load the additional books dataset
books1 = pd.read_csv('Books1.csv')

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create the database tables inside the application context
with app.app_context():
    db.create_all()
@app.route('/')
def admin():
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == '1234566@gmail.com' and password == '12345':
            session['admin'] = True
            return redirect(url_for('admin_dashboard'))  # Redirect to admin_dashboard route
        else:
            return render_template('admin_login.html', message='Invalid email or password')
    else:
        return render_template('admin_login.html', message='')

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' in session:
        all_books = books.to_dict(orient='records')
        return render_template('admin_dashboard.html', books=all_books)
    else:
        return redirect(url_for('admin_login'))


@app.route('/admin/add_book', methods=['GET', 'POST'])
def add_book():
    if 'admin' in session:
        if request.method == 'POST':
            new_book = {
                'id': request.form['id'],
                'title': request.form['title'],
                'author': request.form['author'],
                'description': request.form['description'],
                'genre': request.form['genre'],
                'publication_date': request.form['publication_date'],
                'cover_image_url': request.form['cover_image_url'],
                'pages': request.form['pages'],
                'rating': request.form['rating']
            }
            # Check if the book ID already exists
            if books['id'].isin([new_book['id']]).any():
                flash('Book with ID already exists', 'error')
                return redirect(url_for('add_book'))
            # Add the new book to the CSV file
            with open('Books1.csv', 'a', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=new_book.keys())
                writer.writerow(new_book)

            flash('Book added successfully', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            return render_template('add_book.html')
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/logout')
def admin_logout():
    if 'admin' in session:
        session.pop('admin', None)
    return redirect(url_for('admin_login'))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
