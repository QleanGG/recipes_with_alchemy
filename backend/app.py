from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'my_secret_key'

# SQLAlchemy configuration

# app.config['SQLALCHEMY_DATABASE_URI'] = 'mssql+pyodbc://user1:123@server/restaurant?driver=SQL+Server'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:123@localhost/restaurant'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define Models
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    ingredients = db.Column(db.String(200))
    cooking_time = db.Column(db.String(100))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)


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

@app.route('/remove/<int:id>', methods=['GET', 'POST'])
def remove_recipe(id):
    recipe_to_delete = Recipe.query.get(id)
    if recipe_to_delete:
        db.session.delete(recipe_to_delete)
        db.session.commit()
        flash('Recipe deleted successfully', 'success')
    else:
        flash('Recipe not found', 'error')
    return redirect('/recipes')
    
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_recipe(id):
    recipe_to_edit = Recipe.query.get(id)
    if request.method == 'POST':
        recipe_to_edit.name = request.form['name']
        recipe_to_edit.ingredients = request.form['ingredients']
        recipe_to_edit.cooking_time = request.form['cooking_time']
        try:
            db.session.commit()
            flash('Recipe updated successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating recipe: {str(e)}', 'error')
        return redirect('/recipes')

    return render_template('edit_recipe.html', recipe=recipe_to_edit)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            session['user_id'] = user.id
            flash('Logged in successfully', 'success')
            return redirect('/')
        else:
            flash('Invalid credentials', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username is already taken', 'error')
        else:
            # Create a new user and add to the database
            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Account created successfully', 'success')
            return redirect('/login')

    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
