import os
from datetime import datetime
import random
import string
from flask import Flask, render_template, request, redirect, send_from_directory, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'my_secret_key'

def generate_unique_filename(filename):
    # Get the file extension from the original filename
    file_extension = filename.rsplit('.', 1)[1]
    
    # Generate a random string of characters
    random_string = ''.join(random.choices(string.ascii_letters + string.digits, k=8))

    # Create a unique filename by combining timestamp and random string
    unique_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{random_string}.{file_extension}"
    
    return unique_filename


# upload folder declaration
app.config['UPLOAD_FOLDER'] = 'uploads'

#form declaration
class RecipeForm(FlaskForm):
    name = StringField("Recipe Name", validators=[DataRequired()])
    ingredients = TextAreaField("Ingredients", validators=[DataRequired()])
    cooking_time = StringField("Cooking Time", validators=[DataRequired()])
    image = FileField("Recipe Image", validators=[FileAllowed(['jpg', 'png', 'jpeg', 'gif'], 'Images only!')])

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
    image_path = db.Column(db.String(255))

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

def __init__(self, name, ingredients, cooking_time, image_filename=None):
    self.name = name
    self.ingredients = ingredients
    self.cooking_time = cooking_time
    self.image_path = image_filename

# Create the 'recipes' database if it doesn't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/add', methods=['GET', 'POST'])
def add_recipe():
    form = RecipeForm()

    if form.validate_on_submit():
        name = form.name.data
        ingredients = form.ingredients.data
        cooking_time = form.cooking_time.data
        image = form.image.data

        # Handle the file upload
        if image:
            filename = secure_filename(image.filename)
            unique_filename = generate_unique_filename(filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], unique_filename))
        else:
            filename = None

        # Create a new recipe with the image filename
        new_recipe = Recipe(name=name, ingredients=ingredients, cooking_time=cooking_time, image_path=unique_filename)
        db.session.add(new_recipe)
        db.session.commit()
        flash('Recipe added successfully', 'success')
        return redirect('/recipes')

    return render_template('add_recipe.html', form=form)


#------------------------------------------------------
    
   
@app.route('/recipes')
def show_recipes():
    if 'user_id' in session:
        recipes = Recipe.query.all()
        return render_template('recipes.html', recipes=recipes)
    return redirect(url_for('login'))

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
            session['user_name'] = user.username
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

@app.route('/logout')
def logout():
    flash('Logged out successfully', 'success')
    session.clear()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
