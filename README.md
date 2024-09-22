# Book Recommendation System
A web app that allows users to input the title of a book they have read and gives recommendations based on genre. There is also a popular books section that recommends a list of books based on the genre clicked on.




This is a flask app built with python
- **Frontend:** HTML, CSS
- **Backend:** python, flask, Jinja

# Getting Started
- Clone the repository in your local device.
- Install all the requirements using : ```pip install requirements.txt```
- Code could be run with
```
heroku local web
# or
gunicorn web_flask.app:app
```
- Open with http://0.0.0.0:5000 in your browser to see the web app
## Algorithm used
- CONTENT BASED FILTERING: Content based recommender systems take into account the data provided by the user both directly or indirectly. For example, the book title inputed can the user can be used ot determine books the user may want to read based on the genre of the inputed book title. This type of recommender system relies on characteristics of object. New content can be quickly recommended to the user. These type of systems does not take into account behavior/ data about other users in the systems.

- COSINE SIMILARITY: Cosine similarity is a metric used to measure how similar the documents are irrespective of their size. Mathematically, it measures the cosine of the angle between two vectors projected in a multi-dimensional space. The cosine similarity is advantageous because even if the two similar documents are far apart by the Euclidean distance (due to the size of the document), chances are they may still be oriented closer together. The smaller the angle, higher the cosine similarity.

- Similarity Score : How does it decide which item is most similar to the item the user likes? Here come the similarity scores.

  - It is a numerical value ranges between zero to one which helps to determine how much two items are similar to each other on a scale of zero to one. This similarity score is obtained measuring the similarity between the text details of both of the items. So, similarity score is the measure of similarity between given text details of two items. This can be done by cosine-similarity.
  K-Nearest Neighbors (KNN) identifies books similar to a user's preferences by finding books with similar rating patterns. It calculates the distance between items or users and recommends books based on the closest "neighbors."

Singular Value Decomposition (SVD) is a matrix factorization technique that breaks down the user-book rating matrix into latent factors, helping to predict missing ratings and provide recommendations by capturing hidden relationships between users and books.
 