import os
import math
import re
from flask import (Flask, render_template, redirect, request, url_for, flash,
                   session)
from flask_pymongo import PyMongo, pymongo  # Flask connect to MongoDB Atlas
from bson.objectid import ObjectId
from forms import LoginForm, RegistrationForm, RecipeForm
from werkzeug.security import generate_password_hash, check_password_hash
"""
MongoDB represents JSON documents in binary-encoded format called
BSON behind the scenes. BSON extends the JSON model to provide
additional data types, ordered fields, and to be efficient
for encoding and decoding within different languages.
"""

app = Flask(__name__)

"""
Environment variables SECRET and MONGO_URI set in Heroku
dashboard in production.
"""
app.secret_key = os.getenv("SECRET")
app.config["MONGO_URI"] = os.getenv("MONGO_URI")
app.config["MONGO_DBNAME"] = "virtual_cookbook"
mongo = PyMongo(app)


@app.route('/')
def index():
    """
    Route allows users to view all the recipes within the database
    collection with pagination, logged in users can view profile and create
    recipes.
    """
    page_limit = 6  # Logic for pagination
    current_page = int(request.args.get('current_page', 1))
    total = mongo.db.tasks.count()
    pages = range(1, int(math.ceil(total / page_limit)) + 1)
    task = mongo.db.tasks.find().sort('_id', pymongo.ASCENDING).skip(
        (current_page - 1)*page_limit).limit(page_limit)

    if 'logged_in' in session:
        current_user = mongo.db.user.find_one({'name': session[
            'username'].title()})
        return render_template('index.html', tasks=task,
                               title='Home', current_page=current_page,
                               pages=pages, current_user=current_user)
    else:
        return render_template('index.html', tasks=task,
                               title='Home', current_page=current_page,
                               pages=pages)


@app.route('/get_meat', methods=['GET'])
def meat():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("meat.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Meat Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Meat"}))


@app.route('/get_poultry', methods=['GET'])
def poultry():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("poultry.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Poultry Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Poultry"}))


@app.route('/get_fish', methods=['GET'])
def fish():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("fish.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Fish Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Fish"}))


@app.route('/get_veg', methods=['GET'])
def veg():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("veg.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Vegetable Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Vegetables"}))


@app.route('/get_grains', methods=['GET'])
def grains():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("grains.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Grains Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Grains"}))


@app.route('/get_pasta', methods=['GET'])
def pasta():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("pasta.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           page_title="Pasta Recipes",
                           tasks=mongo.db.tasks.find
                           ({"category_name": "Pasta"}))


@app.route('/get_task/<tasks_id>', methods=['GET', 'POST'])
def task(tasks_id):
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    """
    Route for viewing a single recipe in detail.
    """
    a_recipe = mongo.db.tasks.find_one_or_404({"_id": ObjectId(tasks_id)})
    
    if 'logged_in' in session:
        current_user = mongo.db.user.find_one({
            'name': session['username'].title()})
        return render_template('recipe.html',
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           task=a_recipe, current_user=current_user,
                           title=a_recipe['recipe_name'])
    else:
        return render_template('recipe.html',
                               task=a_recipe, title=a_recipe['recipe_name'])


@app.route('/get_tasks')
def get_tasks():
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("tasks.html",
                           count_tasks=count_tasks,
                           favourite_count=favourite_count,
                           tasks=mongo.db.tasks.find())


@app.route('/add_task', methods=['GET', 'POST'])
def add_tasks():
    """
    Add a new recipe to mongodb database collection
    """
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    # Allows task categories in MongoDB to connect with addtask.html file
    if 'logged_in' not in session:  # Check for user logged in
        flash('Apologies, only logged in users can add recipes.')
        return redirect(url_for('index'))
        
    form = RecipeForm(request.form)  # Initialise the form
    user = mongo.db.user.find_one({"name": session['username'].title()})
    
    if form.validate_on_submit():  # Insert new recipe if form is submitted
        task = mongo.db.tasks
        task.insert_one({
                            'category_name': request.form['category_name'],
                            'complexity': request.form['complexity'],
                            'recipe_name': request.form['recipe_name'],
                            'author_name': request.form['author_name'],
                            'prep_time_mins': int(request.form['prep_time_mins']),
                            'cook_time_mins': int(request.form['cook_time_mins']),
                            'calories': int(request.form['calories']),
                            'servings': int(request.form['servings']),
                            'brief_description': request.form['brief_description'],
                            'ingredients': request.form['ingredients'],
                            'instructions': request.form['instructions'],
                            'recipe_image': request.form['recipe_image'],
                            'favourite': 'favourite' in request.form,
                            'username': session['username'].title(),
                            'created_by': {
                                '_id': user['_id'],
                                'name': user['name']}})
        flash('Recipe Added!')
        return redirect(url_for('index'))
    return render_template('addrecipe.html', count_tasks=count_tasks,
                           favourite_count=favourite_count, 
                           form=form, title="Add New Recipe")
    

@app.route('/insert_tasks', methods=['POST'])
def insert_tasks():
    tasks = mongo.db.tasks  # This is the tasks collection
    tasks.insert_one(request.form.to_dict())
    # when submitting info to URI, its submmited in form of a request object
    return redirect(url_for('index'))
    """
    We then grab the request object, show me the form & convert
    form to dict for Mongo to understand.
    """


@app.route('/edit_task/<task_id>', methods=['GET', 'POST'])
def edit_task(task_id):
    count_tasks = mongo.db.tasks.find().count()
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    if 'logged_in' not in session:  # Check if its a logged in user
        flash('Apologies, only logged in users can edit recipes.')
        return redirect(url_for('index'))
        
    user = mongo.db.user.find_one({"name": session['username'].title()})
    task = mongo.db.tasks.find_one_or_404({"_id": ObjectId(task_id)})
    form = RecipeForm()
    """
    Find a particular task, parameter passed is 'id', looking
    for a match to 'id' in MongoDB, then wrapped for editing
    purposes.
    Reuse much of the layout in 'add_tasks' function,
    but with pre-populated fields.
    """
    if user['name'].title() == task['username'].title():
        if request.method == 'GET':
            form = RecipeForm(data=task)
            return render_template('editrecipe.html', task=task,
                                   count_tasks=count_tasks,
                                   favourite_count=favourite_count,
                                   form=form, title="Edit Recipe")
        if form.validate_on_submit():
            tasks = mongo.db.tasks  # Access to the tasks collection in mongo.db  
            tasks.update_one({
                '_id': ObjectId(task_id),
            }, {
                '$set': {
                            'category_name': request.form['category_name'],
                            'complexity': request.form['complexity'],
                            'recipe_name': request.form['recipe_name'],
                            'author_name': request.form['author_name'],
                            'prep_time_mins': int(request.form['prep_time_mins']),
                            'cook_time_mins': int(request.form['cook_time_mins']),
                            'calories': int(request.form['calories']),
                            'servings': int(request.form['servings']),
                            'brief_description': request.form['brief_description'],
                            'ingredients': request.form['ingredients'],
                            'instructions': request.form['instructions'],
                            'recipe_image': request.form['recipe_image'],
                            'favourite': 'favourite' in request.form
                                                           }})
            flash('Recipe updated.')
            return redirect(url_for('task', task_id=task_id))
    flash("Apologies, this is not your recipe to edit!")
    return redirect(url_for('task', tasks_id=task_id))


@app.route('/delete_task/<task_id>')
def delete_task(task_id):
    """
    We access the tasks collection & call to delete selected task.
    """
    if session:
        user = mongo.db.user.find_one({"name": session['username'].title()})
        task = mongo.db.tasks.find_one_or_404({
                                                '_id': ObjectId(task_id)})
    
        if user['name'].title() == task['username'].title():
            tasks = mongo.db.tasks
            tasks.delete_one({
                '_id': ObjectId(task_id)
            })
            flash('Recipe now deleted')
            return redirect(url_for('index'))
    
        flash("Apologies, this is not your recipe to edit!")
        return redirect(url_for('task', tasks_id=task_id))
    else:
        flash('Apologies, logged in users can only view this page')
        return redirect(url_for('index'))


@app.route('/count_tasks')  # Enables the total recipe counter
def count_tasks():
    count_tasks = mongo.db.tasks.find().count()
    return render_template("index.html",
                           count_tasks=count_tasks)


@app.route('/favourite_count')  # Enables the favourite recipe counter
def favourite_count():
    favourite_count = mongo.db.tasks.find({'favourite': True}).count()
    return render_template("index.html",
                           favourite_count=favourite_count)
                           

@app.errorhandler(404)
# 404 error message supports user when Virtual Cookbook incorrectly renders 
def page_not_found(e):
    """Route for handling 404 errors"""
    return render_template('404.html',
                           title="Page Not Found!"), 404


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Function for handling the registration of users"""
    if 'logged_in' in session:  # Check is user already logged in
        return redirect(url_for('index'))

    form = RegistrationForm()
    if form.validate_on_submit():

        user = mongo.db.user
        dup_user = user.find_one({'name': request.form['username'].title()})

        if dup_user is None:
            hash_pass = generate_password_hash(request.form['password'])
            user.insert_one({'name': request.form['username'].title(),
                             'pass': hash_pass})
            session['username'] = request.form['username']
            session['logged_in'] = True
            return redirect(url_for('index'))

        flash('Apologies, this username already taken. Please try another.')
        return redirect(url_for('register'))
    return render_template('register.html', form=form, title="Register")


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """Function for User login to Virtual Cookbook"""
    if 'logged_in' in session:  # Check is already logged in
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = mongo.db.user
        logged_in_user = user.find_one({
                                'name': request.form['username'].title()})

        if logged_in_user:
            if check_password_hash(logged_in_user['pass'],
                                   request.form['password']):
                session['username'] = request.form['username']
                session['logged_in'] = True
                return redirect(url_for('index'))
            flash('Apologies, password is incorrect!')
            return redirect(url_for('user_login'))
    return render_template('login.html', form=form, title='Login')


@app.route('/logout')
def logout():
    """Logs the user out and redirects to home"""
    session.clear()  # End the session
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(host=os.environ.get('IP', "0.0.0.0"),
            port=int(os.environ.get('PORT', "5000")),
            debug=True)
