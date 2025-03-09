'''
pip install flask
pip install werkzeug
pip install flask-login
pip install authlib

'''

import os
import sqlite3
from flask import Flask, request, redirect, url_for, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "Big_Body_Rosh")

# Flask-Login setup
login_manager = LoginManager(app)

# Database setup
DATABASE = "users.db"

def get_db():
    """Connect to the SQLite database."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # Enables column access by name
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Close the database connection when the request ends."""
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

def create_users_table():
    """Create the users table if it doesn't exist."""
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        """)
        conn.commit()

# Ensure the users table exists
create_users_table()

class User(UserMixin):
    """User class for Flask-Login."""
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    """Load user from the database by user_id."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if user:
        return User(user["id"], user["username"])
    return None

@app.route("/")
def login_page():
    """Login Page with a button to go to the Registration Page."""
    error_message = session.pop("error", None)

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Login</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            form, .redirect-container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 300px; margin: 10px; text-align: center; }}
            h1 {{ text-align: center; color: #333; }}
            label {{ margin-bottom: 8px; display: block; }}
            input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; }}
            input[type="submit"], .register-button {{ background-color: #007BFF; color: #fff; padding: 10px; border: none; border-radius: 4px; cursor: pointer; width: 100%; margin-bottom: 10px; }}
            .message {{ text-align: center; margin: 10px 0; color: red; }}
        </style>
    </head>
    <body>
        <form action="/login" method="post">
            <h1>Login</h1>
            <label for="username">Username:</label>
            <input type="text" name="username" required>
            <label for="password">Password:</label>
            <input type="password" name="password" required>
            <input type="submit" value="Login">
        </form>
        <div class="redirect-container">
            <p>Don't have an account?</p>
            <a href="/register"><button class="register-button">Register</button></a>
        </div>
        {"<div class='message'>" + error_message + "</div>" if error_message else ""}
    </body>
    </html>
    """

@app.route("/register")
def register_page():
    """Registration Page with a back button to the Login Page."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Register</title>
        <style>
            body {{ font-family: Arial, sans-serif; background-color: #f4f4f4; display: flex; align-items: center; justify-content: center; height: 100vh; margin: 0; }}
            form, .redirect-container {{ background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1); width: 300px; margin: 10px; text-align: center; }}
            h1 {{ text-align: center; color: #333; }}
            label {{ margin-bottom: 8px; display: block; }}
            input[type="text"], input[type="password"] {{ width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ddd; border-radius: 4px; }}
            input[type="submit"], .login-button {{ background-color: #28a745; color: #fff; padding: 10px; border: none; border-radius: 4px; cursor: pointer; width: 100%; margin-bottom: 10px; }}
        </style>
    </head>
    <body>
        <form action="/register-user" method="post">
            <h1>Register</h1>
            <label for="new_username">Username:</label>
            <input type="text" name="new_username" required>
            <label for="new_password">Password:</label>
            <input type="password" name="new_password" required>
            <input type="submit" value="Register">
        </form>
        <div class="redirect-container">
            <p>Already have an account?</p>
            <a href="/"><button class="login-button">Go to Login</button></a>
        </div>
    </body>
    </html>
    """

@app.route("/login", methods=["POST"])
def login():
    """Handles user login."""
    username = request.form.get("username")
    password = request.form.get("password")

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user["password"], password):
        login_user(User(user["id"], username))
        return redirect("http://127.0.0.1:5000/")  # Redirect to main website
    else:
        session["error"] = "Invalid credentials, please try again!"
        return redirect(url_for("login_page"))

@app.route("/register-user", methods=["POST"])
def register():
    """Handles new user registration."""
    username = request.form.get("new_username")
    password = request.form.get("new_password")

    if not username or not password:
        session["error"] = "All fields are required!"
        return redirect(url_for("register_page"))

    hashed_password = generate_password_hash(password)

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        session["success"] = "Registration successful! You can now log in."
    except sqlite3.IntegrityError:
        session["error"] = "Username already exists! Please choose another."

    return redirect(url_for("login_page"))

@app.route("/logout")
@login_required
def logout():
    """Logs the user out."""
    logout_user()
    return redirect(url_for("login_page"))

if __name__ == "__main__":
    app.run(debug=True, port=5001)
