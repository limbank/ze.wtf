from flask import Blueprint, render_template, current_app, session, send_file, redirect, url_for, request, make_response, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher
from captcha.image import ImageCaptcha
import os
import json
from dotenv import load_dotenv
from datetime import datetime

from utils.cookies import create_cookie
from utils.crud import check_invite
from utils.general import random_string, check_argon

from utils.auth import authenticate

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

        # Construct login cookie
        new_cookie = create_cookie(user)

        return dict(msg = "Logged in!", cookie=new_cookie, success = True)

    else:
        return dict(msg = "Missing username or password!", success = False)

def register_user():
    # Check captcha
    captcha_valid = check_captcha()
    if captcha_valid['success'] == False:
        return captcha_valid

    # Check invite
    invite_valid = check_invite()
    if invite_valid['success'] == False:
        return invite_valid

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

        # Check if username is allowed
        with open('utils/usernames.json') as f:
            data = json.load(f)
            if username.lower() in data['usernames']:
                return dict(msg = "Username not allowed", success = False)

        # Check username
        user = User.get_or_none(User.username == username)
        if user is not None:
            # User already exists
            return dict(msg = "User already exists", success = False)

        # Hash password
        phash = ph.hash(password + current_app.secret_key)

        # Add user to database
        new_user = User.create(username=username, password=phash, date_joined=datetime.now())

        # Mark invite as used
        invite = Invites.get(Invites.code == request.form['invite'])
        invite.used_by = new_user.users_id
        invite.save()

        # Construct login cookie
        new_cookie = create_cookie(new_user)

        return dict(msg = "Registered!", cookie=new_cookie, success = True)
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

@auth.route("/auth/login/", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def handle_login():
    if g.current_user is not None:
        return redirect(url_for('dash.handle_dash'))

    if request.method == 'POST':
        check_auth = authenticate_user()

        if check_auth['success']:
            # User authenticated, set cookie, then redirect...

            response = make_response(redirect(url_for('dash.handle_dash')))
            response.set_cookie('loggedin', check_auth['cookie'], secure=True, httponly=True, samesite='Lax')

            return response
        else:
            return render_template("login.html", msg=check_auth['msg'])

    return render_template("login.html", msg='')

@auth.route("/auth/register", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def handle_register():
    if g.current_user is not None:
        return redirect(url_for('dash.handle_dash'))

    if request.method == 'POST':
        check_reg = register_user()

        if check_reg['success']:
            # User registered, set cookie, then redirect...

            response = make_response(redirect(url_for('dash.handle_dash')))
            response.set_cookie('loggedin', check_reg['cookie'], secure=True, httponly=True, samesite='Lax')

            return response
        else:
            return render_template("register.html", msg=check_reg['msg'])

    return render_template("register.html", msg='')

@auth.route("/auth/")
@limiter.limit("2/second")
@authenticate
def handle_auth():
    if g.current_user == None:
        return redirect(url_for('auth.handle_login'))
    else: 
        return redirect(url_for('dash.handle_dash'))
