from flask import request, jsonify, g
from datetime import datetime, timedelta
from argon2 import PasswordHasher
from functools import wraps

from models import User, Key, Cookie

ph = PasswordHasher()

def check_argon(chash, value):
    try:
        return ph.verify(chash, value)
    except VerifyMismatchError:
        return False

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
            # To-do, invalidate cookie if the hash verification fails
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