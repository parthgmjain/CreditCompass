import os
from flask import Flask, request, redirect, url_for, session
from authlib.integrations.flask_client import OAuth
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "Big_Body_Rosh")

login_manager = LoginManager(app)
users = {'testuser': generate_password_hash('password')}

class User(UserMixin): 
    pass 

@login_manager.user_loader
def load_user(user_id): 
    user = User()
    user.id = user_id
    return user

# Auth0 Configuration (Use environment variables)
oauth = OAuth(app)
auth0 = oauth.register(
    'auth0',
    client_id = 'YmAa7n9SdQJrZIsZp9oBSGUBbny8pyrW',
    client_secret = 'CGMpkwsA3G6HPmSDWGTfxXbX-gUvt5gzpoKc_IVanLL8MN7SNDlGdPtBNPuS0w9x',
    api_base_url='https://dev-wom4pdox52q73bcy.us.auth0.com',
    access_token_url='https://dev-wom4pdox52q73bcy.us.auth0.com/oauth/token',
    authorize_url='https://dev-wom4pdox52q73bcy.us.auth0.com/authorize',
    client_kwargs={'scope': 'openid profile email'}
)

@app.route('/')
def index():
    """Home Page with Login Options"""
    error_message = session.pop('error', None)  # Gets the error and removes it
    html_error = f'<div style="color: red; text-align: center;">{error_message}</div>' if error_message else ''

    return f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login Page</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                display: flex;
                align-items: center;
                justify-content: center;
                height: 100vh;
                margin: 0;
            }}

            form {{
                background-color: #fff;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                width: 300px;
            }}

            h1 {{
                text-align: center;
                color: #333;
            }}

            label {{
                margin-bottom: 8px;
                display: block;
            }}

            input[type="text"], input[type="password"] {{
                width: 100%;
                padding: 10px;
                margin-bottom: 15px;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}

            input[type="submit"] {{
                background-color: #007BFF;
                color: #fff;
                padding: 10px 15px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                width: 100%;
                margin-bottom: 10px;
            }}

            a {{
                display: block;
                text-align: center;
                margin-top: 10px;
                color: #007BFF;
                text-decoration: none;
            }}

            p {{
                text-align: center;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <form action="/login_direct" method="post">
            <label for="username">Username:</label>
            <input type="text" name="username" id="username" required>

            <label for="password">Password:</label>
            <input type="password" name="password" id="password" required>

            {html_error}

            <input type="submit" value="Login Directly">
            <p>OR</p>
            <a href="/login">Login via SSO</a>
        </form>
    </body>
    </html>
    '''

@app.route('/login')
def login():
    """Login using Auth0 SSO"""
    return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/callback')

@app.route('/callback')
def callback_handling():
    """Auth0 Callback: Handles login response"""
    try:
        resp = auth0.authorize_access_token()
        user_info = auth0.get("userinfo").json()  # Fetch user details
        session['jwt_payload'] = user_info  # Store user details in session

        user = User()
        user.id = user_info['sub']  # Unique identifier from Auth0
        login_user(user)

        return redirect('http://127.0.0.1:5000/')
    except Exception as e:
        session['error'] = "SSO Login Failed. Please try again."
        return redirect(url_for('index'))

@app.route('/login_direct', methods=['POST'])
def login_direct():
    """Handles manual login with username and password"""
    username = request.form.get('username')
    password = request.form.get('password')

    if username in users and check_password_hash(users[username], password):
        user = User()
        user.id = username
        login_user(user)
        return redirect('http://127.0.0.1:5000/')
    
    session['error'] = "Invalid credentials, please try again!"
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """Protected Dashboard Page"""
    return '''
    <h1>Welcome to the Dashboard!</h1>
    <p>You are logged in successfully.</p>
    <a href="/logout">Logout</a>
    '''

@app.route('/logout')
@login_required
def logout():
    """Logs the user out and redirects to home"""
    logout_user()
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True, port = 5001)
