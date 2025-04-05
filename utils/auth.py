from flask import request, jsonify, current_app, session, g
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
from utils.cookies import create_cookie
from utils.general import random_string
from captcha.image import ImageCaptcha
from models import User, Key, Cookie
from argon2 import PasswordHasher
from dotenv import load_dotenv
from functools import wraps
from models import User, Invite
import unicodedata
import json
import re
import os

load_dotenv()

ph = PasswordHasher()

def is_safe_username(username):
    # Normalize Unicode (prevent homoglyph attacks)
    username = unicodedata.normalize("NFKC", username)

    # Remove leading/trailing spaces and invisible characters
    username = username.strip()
    username = ''.join(c for c in username if c.isprintable())

    # Check length constraints
    if not (3 <= len(username) <= 30):
        return False

    # Enforce allowed characters (letters, numbers, _, -)
    if not re.fullmatch(r'^[a-zA-Z0-9_-]+$', username):
        return False

    # Check if username is allowed
    with open('utils/usernames.json') as f:
        data = json.load(f)

        # Check for blocked words
        if any(word in username.lower() for word in data['usernames']):
            return False

    return True

def check_argon(chash, value):
    try:
        return ph.verify(chash, value)
    except VerifyMismatchError:
        return False

def make_captcha():
    captcha_string = random_string(os.getenv('CAPTCHA_LENGTH'))
    session['captcha'] = phash = ph.hash((captcha_string).lower() + current_app.secret_key)

    image = ImageCaptcha(
        width=248,
        height=60,
        fonts=['static/fonts/Inconsolata-Regular.ttf']
    )
    return image.generate(captcha_string)

def check_captcha():
    if 'captcha' in request.form:
        if check_argon(session['captcha'], request.form['captcha'].lower() + current_app.secret_key) == False:
            return dict(msg = "Incorrect captcha!", success = False)
        else:
            return dict(success = True)
    else:
        return dict(msg = "Missing captcha!", success = False)

def check_invite():
    if 'invite' in request.form:
        # Check db for invite
        invite = Invite.get_or_none(Invite.code == request.form['invite'])
        if invite is None:
            # Invite does not exist
            return dict(msg = "You need a valid invite to join!", success = False)

        if invite.used_by is not None:
            # Invite already used
            return dict(msg = "Invite has already been used!", success = False)

        if datetime.now() > invite.expires:
            # Invite already expired
            return dict(msg = "Invite has expired!", success = False)

        return dict(msg = "Invite valid!", success = True)
    else:
        return dict(msg = "Missing invite code", success = False)

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

        if not is_safe_username(username):
            return dict(msg = "Username not allowed", success = False)

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
        new_user = User.create(username=username, password=phash, date_joined=datetime.now())

        # Mark invite as used
        invite = Invite.get(Invite.code == request.form['invite'])
        invite.used_by = new_user.users_id
        invite.save()

        # Construct login cookie
        new_cookie = create_cookie(new_user)

        return dict(msg = "Registered!", cookie=new_cookie, success = True)
    else:
        return dict(msg = "Missing username or password!", success = False)

def check_cookie():
    cookie_token = request.cookies.get('loggedin')

    if cookie_token is not None:
        cookie_details = cookie_token.split('.')

        cookie = Cookie.get_or_none(Cookie.cookie_token == cookie_details[0])
        return cookie

        # Check cookie expiration 
        if datetime.now() > cookie.expires:
            return None

        # Validate cookie
        try:
            ph.verify(cookie.cookie_hash, cookie_details[1] + request.remote_addr)
        except:
            # Cookie invalid
            return None

        return cookie
    else:
        return None

def user_from_cookie(cookie):
    if cookie is None:
        # No cookie
        return None

    current_user = User.get(User.users_id == cookie.user_id)
    return dict(username=current_user.username, user_id=current_user.users_id, role=current_user.role)

def user_from_token(token):
    if token is None:
        # No token
        return None

    # Validate key
    key_records = Key.select().where(Key.expires.is_null(True) | (Key.expires > datetime.now()))

    for key in key_records:
        if check_argon(key.value, token):  # Check hashed key
            # Key verified, get user here
            current_user = User.get(User.users_id == key.owner)
            return dict(username=current_user.username, user_id=current_user.users_id, role=current_user.role)

def check_token():
    auth_header = request.headers.get('Authorization')

    if auth_header is None or auth_header == "":
        return None

    try:
        token = auth_header.split()[1]

        return token
    except:
        return None

def authenticate(f):
    """Decorator to authenticate user and store in Flask's `g` object."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'current_user' not in g:
            g.current_user = None  # Default: no user

            # Try token authentication first
            token = check_token()
            if token:
                g.current_user = user_from_token(token)
            else:
                # Fallback to cookie authentication
                cookie = check_cookie()
                if cookie:
                    g.current_user = user_from_cookie(cookie)

        return f(*args, **kwargs)  # No need to pass user explicitly

    return decorated_function