from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import DataRequired
import requests



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap(app)

# create db
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///movies_2.db"
# Optional: But it will silence the deprecation warning in the console.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class MyForm(FlaskForm):
    rating = FloatField(label='Your Rating Out of 10 e.g 7.5', validators=[DataRequired()])
    review = StringField(label='Your Review')
    done = SubmitField(label='Done')


class AddMovie(FlaskForm):
    movie = StringField(label='Movie Title')
    add_movie = SubmitField(label='Add Movie')


# create table
class Movies(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float, nullable=True)
    ranking = db.Column(db.Integer, nullable=True)
    review = db.Column(db.String(250), nullable=True)
    img_url = db.Column(db.String(250), nullable=False)

    # Optional: this will allow each book object to be identified by its title when printed instead of id which is default.
    def __repr__(self):
        return f'<Book {self.title}>'


db.create_all()




@app.route("/")
def home():
    all_movies = Movies.query.order_by(Movies.rating).all()
    for i in range(len(all_movies)):
    # This line gives each movie a new ranking reversed from their order in all_movies
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)


@app.route('/edit', methods=['GET', 'POST'])
def edit():
    update_form = MyForm()
    movie_id = request.args.get("id")
    movie = Movies.query.get(movie_id)
    if update_form.validate_on_submit():
        # movie = Movies.query.filter_by(id).first()
        # movie.rating = update_form.rating.data
        # movie.review = update_form.review.data
        movie.rating = float(update_form.rating.data)
        movie.review = update_form.review.data
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('edit.html', form=update_form)


@app.route('/delete<int:id>')
def delete(id):
    # movie_id = request.args.get("id")
    # movie = Movies.query.get(movie_id)
    movie = Movies.query.filter_by(id=id).first()
    db.session.delete(movie)
    db.session.commit()
    return redirect(url_for('home'))


@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovie()
    if form.validate_on_submit():
        response = requests.get('https://api.themoviedb.org/3/search/movie',
                                params={"api_key": '4d5c4f7df0436662746a8351c929f72f', "query": form.movie.data})
        result = response.json()['results']
        return render_template('select.html', movies=result)

    return render_template('add.html', form=form)


@app.route('/append')
def append():
    overview = request.args.get('description')
    title = request.args.get('title')
    release_date = request.args.get('year')
    img = request.args.get('img')

    the_movie = Movies(title=title,img_url=f'https://image.tmdb.org/t/p/w500{img}',year=release_date,description=overview)

    db.session.add(the_movie)
    db.session.commit()
    movie = Movies.query.filter_by(title=title).first()
    return redirect(url_for('edit', id=movie.id))


if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
