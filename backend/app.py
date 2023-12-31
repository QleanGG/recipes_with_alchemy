from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# SQLAlchemy configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123@localhost/restaurant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class Recipe(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(200))
    cooking_time = db.Column(db.String(100))

# Create the 'recipes' database if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    # if not session.get('logged_in'):
    # return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        ingredients = request.form['ingredients']
        cooking_time = request.form['cooking_time']

        new_recipe = Recipe(name=name, ingredients=ingredients, cooking_time=cooking_time)
        db.session.add(new_recipe)
        db.session.commit()
        return redirect('/recipes')
    return render_template('add_recipe.html')

@app.route('/recipes')
def show_recipes():
    recipes = Recipe.query.all()
    return render_template('recipes.html', recipes=recipes)

if __name__ == '__main__':
    app.run(debug=True)
