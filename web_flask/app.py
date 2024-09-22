from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from math import sqrt
import hashlib
import secrets
import re
import csv

app = Flask(__name__)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.secret_key = secrets.token_hex(16)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'

db = SQLAlchemy(app)

# Load the original books dataset
books = pd.read_csv('books_data.csv')

# Load the additional books dataset
books1 = pd.read_csv('Books1.csv')

# Concatenate the two datasets
books = pd.concat([books, books1], ignore_index=True)

# Combine the genres for each book
genres_combined = books['genre'].apply(lambda x: ' '.join(eval(x)))

# Create a TfidfVectorizer object to transform the book genres into a Tf-idf representation
tfidf_vectorizer = TfidfVectorizer()
tfidf_matrix = tfidf_vectorizer.fit_transform(genres_combined)

# Use TruncatedSVD for matrix factorization
svd = TruncatedSVD(n_components=50, random_state=42)
svd_matrix = svd.fit_transform(tfidf_matrix)

# Create a NearestNeighbors model
knn_model = NearestNeighbors(n_neighbors=15, metric='cosine')
knn_model.fit(svd_matrix)

# Split the dataset into training and testing sets
train_data, test_data = train_test_split(books, test_size=0.2, random_state=42)

# Train the SVD model on the training set
svd.fit(tfidf_matrix)

# Make predictions on the test set
test_preds = svd.inverse_transform(svd.transform(tfidf_matrix[test_data.index]))

# Calculate RMSE (Root Mean Squared Error) as a measure of accuracy for cosine similarity
cosine_rmse = sqrt(mean_squared_error(cosine_similarity(tfidf_matrix[test_data.index]), cosine_similarity(test_preds)))
print(f"RMSE for Cosine Similarity: {cosine_rmse}")

# Calculate RMSE for SVD
svd_rmse = sqrt(mean_squared_error(tfidf_matrix[test_data.index].toarray(), test_preds))
print(f"RMSE for SVD: {svd_rmse}")


# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

# Create the database tables inside the application context
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Check if email is valid
        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('register.html', message='Invalid email format')
        
        # Check if password is at least 8 characters long and contains both letters and numbers
        if len(password) < 8 or not re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$", password):
            return render_template('register.html', message='Password must be at least 8 characters long and contain both letters and numbers')
        
        # Check if password and confirm password match
        if password != confirm_password:
            return render_template('register.html', message='Passwords do not match')
        
        # Check if the email already exists
        if User.query.filter_by(email=email).first():
            return render_template('register.html', message='Email already exists')
        else:
            # Add the new user to the database
            new_user = User(email=email, password=hashlib.sha256(password.encode()).hexdigest())
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
    else:
        return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(email=email, password=hashlib.sha256(password.encode()).hexdigest()).first()
        if user:
            session['username'] = email  # Store the email in the session
            return render_template('home.html', email=email)
        else:
            return render_template('login.html', message='Invalid email or password')
    else:
        return render_template('login.html', message='')

@app.route('/home')
def home():
    """Route renders the home page"""
    return render_template('home.html')

@app.route('/autocomplete', methods=['POST'])
def autocomplete():
    book_input = request.form.get('book')
    if book_input and books is not None:
        # Filter the books DataFrame to get similar book titles based on the user's input
        similar_books = books[books['title'].str.contains(book_input, case=False)]['title'].tolist()
        return jsonify(similar_books)
    else:
        return jsonify([])  # Return an empty list if no suggestions are available

@app.route('/recommendations', methods=['POST'])
def recommendations():
    """
        Route that renders recommendations post request
    """
    # Retrieve the user input from the form
    book_input = request.form.get('book')

    if book_input:
        try:
            # Find the index of the book in the similarity dataframe
            book_index = books[books['title'] == book_input].index[0]

            # Get the most similar books using the KNN model
            distances, indices = knn_model.kneighbors([svd_matrix[book_index]])

            # Get the top 15 most similar books to the input book
            similar_books_indices = indices[0][1:]
            similar_books = books.iloc[similar_books_indices]['title'].tolist()

            # Retrieve the book details based on the top 15 similar book titles
            recommendations_df = books.loc[books['title'].isin(similar_books)]
            # convert the DataFrame to a list of dictionaries
            recommendations = recommendations_df.to_dict(orient='records')

            return render_template('recommendations.html', recommendations=recommendations, book_input=book_input)
        except IndexError:
            # Handle the case where the book input is not found in the books dataframe
            error_message = "Book not found. Please try again."
            return render_template('error.html', error_message=error_message)

@app.route('/recommendations/book/<int:book_id>')
def book_details(book_id):
    """
        Route gets a specific book based on the id of the book click on from recommendations
    """
    # Define a function to get book by ID
    def get_book_by_id(book_id):
        return books[books['id'] == int(book_id)].iloc[0].to_dict()

    book = get_book_by_id(str(book_id))
    if book:
        return render_template('book_details.html', book=book)
    else:
        # Handle the case when the book is not found, e.g., display an error message
        return render_template('book_not_found.html')

@app.route('/recommendations/genre/<genre>', methods=['GET'])
def genre_recommendations(genre):
    """
        Route that gets the genre recommendation when a
        specific genre is clicked on
    """
    # Filter the books dataframe based on the selected genre
    genre_books = books[books['genre'].str.contains(genre, case=False)]

    # Sort the DataFrame by rating and select the top 15 books
    top_15_books = genre_books.sort_values('rating', ascending=False).head(15)

    return render_template('genre_recommendations.html', genre=genre, books=top_15_books)

if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5000, debug=True)
