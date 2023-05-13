from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    jsonify,
    session,
)
import sqlite3
import os
from datetime import datetime, timedelta
import json

app = Flask(__name__)
app.secret_key = "your_secret_key"
db_path = "database.sqlite"

app.config["FLASH_CATEGORY"] = "now"


# Creation of database
def init_database():
    conn = sqlite3.connect(db_path)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS users (
                        username TEXT PRIMARY KEY,
                        email TEXT,
                        firstName TEXT,
                        lastName TEXT,
                        password TEXT
                        )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS items (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT,
                        title TEXT,
                        description TEXT,
                        category TEXT,
                        price REAL,
                        date TEXT
                        )"""
    )

    conn.execute(
        """CREATE TABLE IF NOT EXISTS reviews (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    item_id INTEGER,
                    rating TEXT,
                    description TEXT,
                    date TEXT
                    )"""
    )
    conn.execute(
        """CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    favorite_user TEXT NOT NULL
                    )"""
    )

    # Create test populations for database initialization
    example_users = [
        ("test1", "test1@gmail.com", "firstName1", "lastName1", "password1"),
        ("test2", "test2@gmail.com", "firstName2", "lastName2", "password2"),
        ("test3", "test3@gmail.com", "firstName3", "lastName3", "password3"),
        ("test4", "test4@gmail.com", "firstName4", "lastName4", "password4"),
        ("test5", "test5@gmail.com", "firstName5", "lastName5", "password5"),
    ]
    try:
        conn.executemany(
            """
            INSERT INTO users (username, email, firstName, lastName, password) VALUES (?, ?, ?, ?, ?);
            """,
            example_users,
        )
    except sqlite3.IntegrityError:
        pass
    conn.commit()
    conn.close()


# MAIN ROUTE START
@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        action = request.form.get("action")
        if action == "signin":
            return handle_signin()
        elif action == "signup":
            return redirect(url_for("handle_signup"))
        elif action == "init_db":
            init_database()
            flash("Database initialized!", app.config["FLASH_CATEGORY"])
    return render_template("signin.html")


from datetime import datetime, timedelta


# Item route
@app.route("/add_item", methods=["GET", "POST"])
def add_item():
    if request.method == "POST":
        username = request.form["username"]
        title = request.form["title"]
        description = request.form["description"]
        category = request.form["category"]
        price = request.form["price"]
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # Searching to validate existing user exists
            c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            count = c.fetchone()[0]
            if count > 0:
                c.execute(
                    "SELECT COUNT(*) FROM items WHERE username = ? AND date BETWEEN ? AND ?",
                    (username, yesterday, today),
                )
                count = c.fetchone()[0]
                if count < 3:
                    c.execute(
                        "INSERT INTO items (username, title, description, category, price, date) VALUES (?, ?, ?, ?, ?, ?)",
                        (username, title, description, category, price, today),
                    )
                    conn.commit()
                    flash("Item added successfully!", app.config["FLASH_CATEGORY"])
                    return render_template("searchbar.html")
                else:
                    flash(
                        "You have reached the maximum limit of 3 posts in a day",
                        app.config["FLASH_CATEGORY"],
                    )
                    return render_template("searchbar.html")
            else:
                flash(
                    "Invalid username. Please enter a valid username.",
                    app.config["FLASH_CATEGORY"],
                )
                return render_template("searchbar.html")
    return render_template("searchbar.html")


# sign in route
@app.route("/signin", methods=["GET", "POST"])
def handle_signin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                "SELECT * FROM users WHERE username=? AND password=?",
                (username, password),
            )
            user = c.fetchone()
            if user is None:
                flash("Invalid username or password!", app.config["FLASH_CATEGORY"])
            else:
                flash("Sign in successful!", app.config["FLASH_CATEGORY"])
                return redirect(
                    url_for(
                        "profile",
                        username=user[0],
                        email=user[1],
                        firstName=user[2],
                        lastName=user[3],
                    )
                )

    return render_template("signin.html")


# profile route
@app.route("/profile/<firstName>/<lastName>/<username>/<email>")
def profile(firstName, lastName, username, email):
    return render_template(
        "profile.html", name=firstName + " " + lastName, username=username, email=email
    )


# signup route
@app.route("/signup", methods=["GET", "POST"])
def handle_signup():
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        firstName = request.form["firstName"]
        lastName = request.form["lastName"]
        password = request.form["password"]
        confirmPassword = request.form["confirmPassword"]

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            c.execute("SELECT * FROM users WHERE username = ?", (username,))
            if c.fetchall():
                flash("Username already exists!", app.config["FLASH_CATEGORY"])
                return redirect(url_for("handle_signup"))

            c.execute("SELECT * FROM users WHERE email = ?", (email,))
            if c.fetchall():
                flash("Email already exists!", app.config["FLASH_CATEGORY"])
                return redirect(url_for("handle_signup"))

            if password != confirmPassword:
                flash("Passwords do not match!", "danger", app.config["FLASH_CATEGORY"])
                return redirect(url_for("handle_signup"))

            c.execute(
                """INSERT INTO users (username, email, firstName, lastName, password) 
                VALUES (?, ?, ?, ?, ?)""",
                (username, email, firstName, lastName, password),
            )
            conn.commit()

            # Will flash a warning when the registration is successful
            flash("Registration successful!", app.config["FLASH_CATEGORY"])
            return redirect(url_for("handle_signin"))

    return render_template("signup.html")


# search route
@app.route("/searchbar", methods=["GET", "POST"])
def searchbar():
    if request.method == "GET":
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT DISTINCT category FROM items")
            categories = [row[0] for row in c.fetchall()]
            return render_template("searchbar.html", categories=categories)

    elif request.method == "POST":
        selected_item_id = request.form.get("selected_item_id")
        if selected_item_id:
            # retrieve the selected item from the database and pass it to selected html page
            with sqlite3.connect(db_path) as conn:
                c = conn.cursor()
                c.execute("SELECT * FROM items WHERE id = ?", (selected_item_id,))
                item = c.fetchone()
                if item:
                    return render_template("selected.html", item=item)

        # if no item was chosen, will redirect to the searchbar template
        return redirect(url_for("searchbar"))


# item search route
@app.route("/search_items", methods=["GET"])
def search_items():
    if request.method == "GET":
        category = request.args.get("category")
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute("SELECT * FROM items WHERE category = ?", (category,))
            items = c.fetchall()
            return render_template("searchbar.html", search_results=items)
    return redirect(url_for("searchbar"))


# specific item route


@app.route("/add_favorite", methods=["GET", "POST"])
def add_favorite():
    if request.method == "POST":
        username = request.form["username"]
        favorite_user = request.form["favorite_user"]
        next_url = request.form.get("next")

        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO favorites (username, favorite_user) VALUES (?, ?)",
                (username, favorite_user),
            )
            conn.commit()

        flash("Favorite added successfully!", app.config["FLASH_CATEGORY"])

        if next_url:
            return redirect(next_url)
        else:
            return redirect(url_for("searchbar"))

    return render_template("searchbar.html")


@app.route("/item/<int:item_id>/")
def item_detail(item_id):
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        c.execute("SELECT * FROM items WHERE id = ?", (item_id,))
        item = c.fetchone()
        if item:
            c.execute("SELECT * FROM reviews WHERE item_id = ?", (item_id,))
            reviews = c.fetchall()
            return render_template("selected.html", item=item, reviews=reviews)
        else:
            return "Item not found", 404


# review route
@app.route("/item/<int:item_id>/submit_review", methods=["GET", "POST"])
def submit_review(item_id):
    if request.method == "POST":
        username = request.form["username"]
        rating = request.form["rating"]
        description = request.form["description"]
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        with sqlite3.connect(db_path) as conn:
            c = conn.cursor()

            # Validating user input for username exists
            c.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
            user_count = c.fetchone()[0]
            if user_count == 0:
                flash(
                    "You must be a registered user to submit a review",
                    app.config["FLASH_CATEGORY"],
                )
                return redirect(url_for("item_detail", item_id=item_id))

            # Fetching username from given item
            c.execute("SELECT username FROM items WHERE id = ?", (item_id,))
            item_username = c.fetchone()[0]
            if username == item_username:
                flash(
                    "You cannot review your own product", app.config["FLASH_CATEGORY"]
                )
                return redirect(url_for("item_detail", item_id=item_id))
            c.execute(
                "SELECT COUNT(*) FROM reviews WHERE username = ? AND date BETWEEN ? AND ?",
                (username, yesterday, today),
            )
            count = c.fetchone()[0]
            if count < 3:
                c.execute(
                    "INSERT INTO reviews (username, item_id, rating, description, date) VALUES (?, ?, ?, ?, ?)",
                    (username, item_id, rating, description, today),
                )
                conn.commit()
                flash("Review submitted successfully!", app.config["FLASH_CATEGORY"])
                return redirect(url_for("item_detail", item_id=item_id))
            else:
                flash(
                    "You have reached the maximum limit of 3 reviews in a day",
                    app.config["FLASH_CATEGORY"],
                )
            return redirect(url_for("item_detail", item_id=item_id))
    return render_template("selected.html")


@app.route("/user_forum", methods=["GET", "POST"])
def user_forum():
    with sqlite3.connect(db_path) as conn:
        c = conn.cursor()
        # Fetch all items from the database
        c.execute("SELECT * FROM items")
        items = c.fetchall()

        # (Part 3: Number 1)
        # Fetch most expensive items
        c.execute("SELECT *, MAX(price) as max_prices FROM items GROUP by category")
        max_prices = c.fetchall()

        # (Part 3: Number 2)
        # Get the two categories entered by the user
        category1 = request.args.get("category1")
        category2 = request.args.get("category2")

        # (Part 3: Number 2)
        # Search for the user who has both categories
        c.execute(
            "SELECT DISTINCT username FROM items WHERE category=? OR category=? GROUP BY username HAVING COUNT(DISTINCT category) = 2",
            (category1, category2),
        )
        users = c.fetchall()

        # (Part 3: Number 3)
        # Get the username entered by the user
        username = request.args.get("username")

        # (Part 3: Number 3)
        # Fetch all reviews from the database for the given username and rating
        c.execute(
            'SELECT id, username, item_id, rating, description, date FROM reviews WHERE username=? AND rating IN ("Excellent", "Great")',
            (username,),
        )
        reviews = c.fetchall()

        # (Part 3: Number 4)
        # List the users who posted the most number of items since 5/1/2020 (inclusive)
        c.execute(
            """SELECT username, COUNT(*) as num_items FROM items
                        WHERE date >= "2020-05-01" GROUP BY username HAVING num_items = (
                            SELECT COUNT(*) FROM items WHERE date >= "2020-05-01"
                            GROUP BY username ORDER BY COUNT(*) DESC LIMIT 1 )"""
        )
        top_users = c.fetchall()

        # (Part 3: Number 5)
        # Fetch all usernames from the database and display them in a dropdown menu
        c.execute("SELECT DISTINCT username FROM favorites")
        usernames = c.fetchall()

        username1 = ""
        username2 = ""

        # Check if both dropdown menus are selected and find the users who have the same favorite user
        if request.method == "POST":
            username1 = request.form["username1"]
            username2 = request.form["username2"]
            c.execute(
                f"""SELECT favorite_user
                    FROM favorites
                    WHERE username = '{username1}'
                    AND favorite_user IN (
                      SELECT favorite_user
                      FROM favorites
                      WHERE username = '{username2}'
                    );
                    """
            )
            common_favorites = c.fetchall()
        else:
            common_favorites = None

    # (Part 3: Number 6)
    # Display all the users who never posted any "excellent" items
    # An item is considered excellent if it has at least 3 reviews of "Excellent"
    c.execute(
        """ select username from users where username not in (SELECT DISTINCT items.username
            FROM items
            LEFT JOIN reviews ON items.id = reviews.item_id
            WHERE reviews.rating = 'Excellent'
            GROUP BY items.id, items.username
            HAVING COUNT(reviews.id) >= 3)
            """
    )
    excellent_users = c.fetchall()

    # (Part 3: Number 7)
    # Fetch all usernames from the database for the given rating of Poor
    c.execute("SELECT username FROM reviews WHERE username NOT IN (SELECT username FROM reviews WHERE rating='Poor') GROUP BY username")
    users2 = c.fetchall()

    # (Part 3: Number 8)
    # Display all the users who posted reviews with a rating of "Poor"
    c.execute('SELECT DISTINCT username FROM reviews WHERE rating = "Poor"')
    poor_review_users = c.fetchall()

    # (Part 3: Number 9)
    # Display users such that each item they posted so far never received any "Poor" reviews
    c.execute('''
            WITH poor_review_users AS (
                SELECT DISTINCT i.username
                FROM items i
                JOIN reviews r ON i.id = r.item_id
                WHERE r.rating = "Poor"
            )
            SELECT DISTINCT i.username
            FROM items i
            WHERE i.username NOT IN (SELECT username FROM poor_review_users)
        ''')
    good_item_users = c.fetchall()
    

    # !(Part 3: Number 10)
    # Get a user pair (A, B) such that they always gave each other "excellent" reviews for every single item they posted

    # c.execute("""select * from items""")
    # print(c.fetchall())

    # Get a user pair (A, B) such that they always gave each other "excellent" reviews for every single item they posted
    c.execute('''SELECT i1.username as user1, i2.username as user2
                    FROM items i1
                    INNER JOIN reviews r1 ON i1.id = r1.item_id AND r1.rating = 'Excellent'
                    INNER JOIN items i2 ON i2.username = r1.username AND i1.id != i2.id
                    INNER JOIN reviews r2 ON i2.id = r2.item_id AND r2.username = i1.username
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM reviews r3
                        WHERE r3.username = i1.username AND r3.item_id = i2.id AND r3.rating != 'Excellent'
                        OR r3.username = i2.username AND r3.item_id = i1.id AND r3.rating != 'Excellent'
                    )''')
    excellent_review_pairs = [list(sorted(x)) for x in c.fetchall()]
    ret = [pair for i, pair in enumerate(excellent_review_pairs) if pair not in excellent_review_pairs[:i]]


    # HOLD ON
    
    # for t in c.fetchall():
    #     print(t)

    # _excellent_review_pairs = [list(sorted(x)) for x in exc]
    # excellent_review_pairs = [
    #     pair
    #     for i, pair in enumerate(_excellent_review_pairs)
    #     if pair not in _excellent_review_pairs[:i]
    # ]
    # print(excellent_review_pairs)

    return render_template(
        "userforum.html",
        item_results=items,
        max_prices=max_prices,
        users=users,
        users2=users2,
        reviews=reviews,
        top_users=top_users,
        excellent_users=excellent_users,
        poor_review_users=poor_review_users,
        good_item_users=good_item_users,
        excellent_review_pairs=ret,
        usernames=usernames,
        username1=username1,
        username2=username2,
        common_favorites=common_favorites,
    )


# clearing messages such as succesful signup/incorrect username etc
@app.route("/clear-flash", methods=["POST"])
def clear_flash():
    session.pop("_flashes", None)
    return "", 204


if __name__ == "__main__":
    init_database()
    app.run()
