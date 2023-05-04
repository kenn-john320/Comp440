from flask import Flask, render_template, request, flash, redirect, url_for, jsonify, session
import sqlite3
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'
db_path = 'database.sqlite'

app.config['FLASH_CATEGORY'] = 'now'

# Creation of database
def init_database():
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        email TEXT,
                        firstName TEXT,
                        lastName TEXT,
                        password TEXT
                        )''')
        conn.execute('''CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        title TEXT,
                        description TEXT,
                        category TEXT,
                        price REAL,
                        date TEXT
                        )''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    item_id INTEGER,
                    rating TEXT,
                    description TEXT,
                    date TEXT
                    )''')

        
        # Create test populations for database initialization
        example_users = [
            ('test1', 'test1@gmail.com','firstName1','lastName1', 'password1'),
            ('test2', 'test2@gmail.com','firstName2','lastName2', 'password2'),
            ('test3', 'test3@gmail.com','firstName3','lastName3', 'password3'),
            ('test4', 'test4@gmail.com','firstName4','lastName4', 'password4'),
            ('test5', 'test5@gmail.com','firstName5','lastName5', 'password5'),
        ]
        conn.executemany('''
        INSERT INTO users (username, email, firstName, lastName, password) VALUES (?, ?, ?, ?, ?);
        ''', example_users)
        conn.commit()
        conn.close()


# MAIN ROUTE START
@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'signin':
            return handle_signin()
        elif action == 'signup':
            return redirect(url_for('handle_signup'))
        elif action == 'init_db':
            init_database()
            flash('Database initialized!', app.config['FLASH_CATEGORY'])
    return render_template('signin.html')

from datetime import datetime, timedelta

#Item route
@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        username = request.form['username']
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # Searching to validate existing user exists
            c.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
            count = c.fetchone()[0]
            if count > 0:
                c.execute('SELECT COUNT(*) FROM items WHERE username = ? AND date BETWEEN ? AND ?', (username, yesterday, today))
                count = c.fetchone()[0]
                if count < 3:
                    c.execute('INSERT INTO items (username, title, description, category, price, date) VALUES (?, ?, ?, ?, ?, ?)', (username, title, description, category, price, today))
                    conn.commit()
                    flash('Item added successfully!', app.config['FLASH_CATEGORY'])
                    return render_template('searchbar.html')
                else:
                    flash('You have reached the maximum limit of 3 posts in a day', app.config['FLASH_CATEGORY'])
                    return render_template('searchbar.html')
            else:
                flash('Invalid username. Please enter a valid username.', app.config['FLASH_CATEGORY'])
                return render_template('searchbar.html')
    return render_template('searchbar.html')


# sign in route
@app.route('/signin', methods=['GET', 'POST'])
def handle_signin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
            user = c.fetchone()
            if user is None:
                flash('Invalid username or password!', app.config['FLASH_CATEGORY'])
            else:
                flash('Sign in successful!', app.config['FLASH_CATEGORY'])
                return redirect(url_for('profile',username=user[0], email=user[1], firstName=user[2], lastName=user[3]))
                
    return render_template('signin.html')

# profile route
@app.route('/profile/<firstName>/<lastName>/<username>/<email>')
def profile(firstName, lastName, username, email):
    return render_template('profile.html', name=firstName + " " + lastName, username=username, email=email)

# signup route
@app.route('/signup', methods=['GET', 'POST'])
def handle_signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            c.execute('SELECT * FROM users WHERE username = ?', (username,))
            if c.fetchall():
                flash('Username already exists!', app.config['FLASH_CATEGORY'])
                return redirect(url_for('handle_signup'))

            c.execute('SELECT * FROM users WHERE email = ?', (email,))
            if c.fetchall():
                flash('Email already exists!', app.config['FLASH_CATEGORY'])
                return redirect(url_for('handle_signup'))

            if password != confirmPassword:
                flash('Passwords do not match!', 'danger', app.config['FLASH_CATEGORY'])
                return redirect(url_for('handle_signup'))

            c.execute('''INSERT INTO users (username, email, firstName, lastName, password) 
                VALUES (?, ?, ?, ?, ?)''', (username, email, firstName, lastName, password))
            conn.commit()

            # Will flash a warning when the registration is successful
            flash('Registration successful!', app.config['FLASH_CATEGORY'])
            return redirect(url_for('handle_signin'))

    return render_template('signup.html')


#search route
@app.route('/searchbar', methods=['GET', 'POST'])
def searchbar():
    if request.method == 'GET':
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT DISTINCT category FROM items')
            categories = [row[0] for row in c.fetchall()]
            return render_template('searchbar.html', categories=categories)

    elif request.method == 'POST':
        selected_item_id = request.form.get('selected_item_id')
        if selected_item_id:
            # retrieve the selected item from the database and pass it to selected html page
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute('SELECT * FROM items WHERE id = ?', (selected_item_id,))
                item = c.fetchone()
                if item:
                    return render_template('selected.html', item=item)
        
        # if no item was chosen, will redirect to the searchbar template
        return redirect(url_for('searchbar'))


#item search route
@app.route('/search_items', methods=['GET'])
def search_items():
    if request.method == 'GET':
        category = request.args.get('category')
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM items WHERE category = ?', (category,))
            items = c.fetchall()
            return render_template('searchbar.html', search_results=items)
    return redirect(url_for('searchbar'))
#specific item route

@app.route('/item/<int:item_id>/')
def item_detail(item_id):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute('SELECT * FROM items WHERE id = ?', (item_id,))
        item = c.fetchone()
        if item:
            c.execute('SELECT * FROM reviews WHERE item_id = ?', (item_id,))
            reviews = c.fetchall()
            return render_template('selected.html', item=item, reviews=reviews)
        else:
            return "Item not found", 404


#review route 
@app.route('/item/<int:item_id>/submit_review', methods=['GET','POST'])
def submit_review(item_id):
    if request.method == 'POST':
        username = request.form['username']
        rating = request.form['rating']
        description = request.form['description']
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # Validating user input for username exists
            c.execute('SELECT COUNT(*) FROM users WHERE username = ?', (username,))
            user_count = c.fetchone()[0]
            if user_count == 0:
                flash('You must be a registered user to submit a review', app.config['FLASH_CATEGORY'])
                return redirect(url_for('item_detail', item_id=item_id))
                
            # Fetching username from given item
            c.execute('SELECT username FROM items WHERE id = ?', (item_id,))
            item_username = c.fetchone()[0]
            if username == item_username:
                flash('You cannot review your own product', app.config['FLASH_CATEGORY'])
                return redirect(url_for('item_detail', item_id=item_id))
            c.execute('SELECT COUNT(*) FROM reviews WHERE username = ? AND date BETWEEN ? AND ?', (username, yesterday, today))
            count = c.fetchone()[0]
            if count < 3:
                c.execute('INSERT INTO reviews (username, item_id, rating, description, date) VALUES (?, ?, ?, ?, ?)', (username, item_id, rating, description, today))
                conn.commit()
                flash('Review submitted successfully!', app.config['FLASH_CATEGORY'])
                return redirect(url_for('item_detail', item_id=item_id))
            else: 
                flash('You have reached the maximum limit of 3 reviews in a day', app.config['FLASH_CATEGORY'])
            return redirect(url_for('item_detail', item_id=item_id))
    return render_template('selected.html')
    

# clearing messages such as succesful signup/incorrect username etc
@app.route('/clear-flash', methods=['POST'])
def clear_flash():
    session.pop('_flashes', None)
    return '', 204


if __name__ == '__main__':
    init_database()
    app.run(debug=True)
