import os
import pprint
import re
from turtle import title
from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import requests

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_top10_movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), nullable=True)
    year = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(250), nullable=True)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=False)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    def __repr__(self) -> str:
        return f'Movie: {self.title}, Rank: {self.ranking}'

# new_movie = Movies(
#                 id=5,
#                 title = "Kung Fu Hustle",     
#                 year = 1999
#                 description = "A very inspiring story",
#                 rating = 8.5,
#                 ranking = 3,
#                 review = "A very good fight in the movie",
#                 img_url = "https://image.tmdb.org/t/p/original/18BmJuz8LgY5GyiRO6H16hN7iWP.jpg"
#             )
# db.session.add(new_movie)
# db.session.commit()
    
@app.route("/")
def home():
    movies = Movies.query.all()

    return render_template("index.html", movies=movies)

class Add_movie(FlaskForm):
    add_movie = StringField("Movie title", validators=[DataRequired()])
    submit = SubmitField("Done")

API_KEY = "123d9cadbf1a654a49e0bb3ef1562be8"
URL = "https://api.themoviedb.org/3/search/movie"
URL2 = "https://api.themoviedb.org/3/movie/{movie_id}"

@app.route("/add", methods=["POST", "GET"])
def add():
    if os.path.isfile('my_top10_movies.db'):
        form = Add_movie(csrf_enabled=False)
        if form.validate_on_submit():
            movie_title = form.add_movie.data
            response = requests.get(url=URL, params={"api_key" : API_KEY, "query": movie_title})
            data = response.json()["results"]
            print(data)
            return render_template('select.html', options=data)
        # else:
        #     return redirect(url_for('home', id=request.args.get('id')))
        return render_template('add.html', form=form)

    else:
        db.create_all()

class Edit_review(FlaskForm):
    rating = StringField("Add new rating for the movie")
    review = StringField("Add a new review here")
    submit = SubmitField("Done")

@app.route('/update', methods=['POST', 'GET'])
def update():
    form = Edit_review(csrf_enabled=False)
    movie_id = request.args.get('id')
    movie_title = request.args.get('title')
    movie_to_update = Movies.query.get(movie_id)
    if form.validate_on_submit():
        movie_to_update.review = form.review.data
        movie_to_update.rating = float(form.rating.data)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', movie=movie_to_update,title=movie_title, form=form)


@app.route('/delete', methods=['GET', 'POST'])
def delete():
    movie_id = request.args.get('id')
    movie_to_delete = Movies.query.get(movie_id)
    db.session.delete(movie_to_delete)
    db.session.commit()
    return redirect(url_for('home'))



if __name__ == '__main__':
    app.run(debug=True, port=5000)
