from flask import Blueprint, render_template, current_app, session, send_file, redirect, url_for, request, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher
from captcha.image import ImageCaptcha
import os
import string
import random
from dotenv import load_dotenv
from datetime import datetime, timedelta

# Change to only import users later
from models import *

load_dotenv()
ph = PasswordHasher()
limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def check_argon(chash, value):
    try:
        ph.verify(chash, value)
        return True
    except:
        return False

def check_captcha():
    if 'captcha' in request.form:
        if check_argon(session['captcha'], request.form['captcha'].lower() + current_app.secret_key) == False:
            return dict(msg = "Incorrect captcha!", success = False)
        else:
            return dict(success = True)
    else:
        return dict(msg = "Missing captcha!", success = False)

def authenticate_user():
    # Check captcha
    captcha_valid = check_captcha()
    if captcha_valid['success'] == False:
        return captcha_valid

    # Check user
    if 'username' in request.form and 'password' in request.form:
        default_msg = "Wrong username or password!"
        # Separating these introduces and easier credential stuffing attack vector
        username = request.form['username']
        password = request.form['password']

        # Check username
        user = User.get_or_none(User.username == username)
        if user is None:
            # User does not exist
            return dict(msg = default_msg, success = False)

        # Check password
        try:
            ph.verify(user.password, password + current_app.secret_key)
        except:
            return dict(msg = default_msg, success = False)

        # TO-DO:
        # Factor in user-agent
        # Move to its own func
        
        # Construct login cookie
        users_ip = request.remote_addr
        users_id = user.users_id
        user_agent = request.headers.get('User-Agent')

        cookie_token = random_string(12)
        cookie_validator = random_string(24)

        cookie_hash = ph.hash(cookie_validator + users_ip)

        # Save cookie to DB
        Cookie.create(user_id=users_id, created=datetime.now(), expires=datetime.now() + timedelta(days=30), cookie_token=cookie_token, cookie_hash=cookie_hash)

        new_cookie = cookie_token + "." + cookie_validator

        return dict(msg = "Logged in!", cookie=new_cookie, success = True)

    else:
        return dict(msg = "Missing username or password!", success = False)

def register_user():
    # Check captcha
    captcha_valid = check_captcha()
    if captcha_valid['success'] == False:
        return captcha_valid

    # Check user
    if 'username' in request.form and 'password' in request.form:
        # Separating these introduces and easier credential stuffing attack vector
        username = request.form['username']
        password = request.form['password']
        password_confirm = request.form['password-confirm']

        # Check passwords
        if password != password_confirm:
            # Passwords dont match
            return dict(msg = "Passwords do not match", success = False)

        # Check username
        user = User.get_or_none(User.username == username)
        if user is not None:
            # User already exists
            return dict(msg = "User already exists", success = False)

        # Hash password
        phash = ph.hash(password + current_app.secret_key)

        # Add user to database
        User.create(username=username, password=phash, date_joined=datetime.now())

        return dict(msg = "Registered!", success = True)
    else:
        return dict(msg = "Missing username or password!", success = False)

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/captcha')
@limiter.limit("2/second")
def dash_captcha():
    captcha_string = random_string(os.getenv('CAPTCHA_LENGTH'))
    session['captcha'] = phash = ph.hash((captcha_string).lower() + current_app.secret_key)

    image = ImageCaptcha(fonts=['static/fonts/Manrope-Regular.woff'])
    data = image.generate(captcha_string)

    return send_file(data, mimetype='image/png')

@auth.route("/auth/login", methods=['GET', 'POST'])
@limiter.limit("2/second")
def handle_login():
    msg = ''

    if request.method == 'POST':
        check_auth = authenticate_user()

        if check_auth['success']:
            # User authenticated, set cookie, then redirect here...

            response = make_response(render_template("login.html", msg=check_auth['msg']))
            response.set_cookie('loggedin', check_auth['cookie'])

            return response
        else:
            return render_template("login.html", msg=check_auth['msg'])

    return render_template("login.html", msg=msg)

@auth.route("/auth/register", methods=['GET', 'POST'])
@limiter.limit("2/second")
def handle_register():
    msg = ''

    if request.method == 'POST':
        check_reg = register_user()

        if check_reg['success']:
            # User registered, redirect here...
            # Temporary
            return render_template("register.html", msg=check_reg['msg'])
        else:
            return render_template("register.html", msg=check_reg['msg'])

    return render_template("register.html", msg=msg)

@auth.route("/auth")
@limiter.limit("2/second")
def handle_auth():
    return redirect(url_for('auth.handle_login'))