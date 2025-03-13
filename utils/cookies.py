from flask import  request
from argon2 import PasswordHasher
from datetime import datetime, timedelta
import random
import string
from models import *

ph = PasswordHasher()

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def create_cookie(user):
    # Construct login cookie
    # TO-DO:
    # Factor in user-agent
    users_ip = request.remote_addr
    users_id = user.users_id
    user_agent = request.headers.get('User-Agent')

    cookie_token = random_string(12)
    cookie_validator = random_string(24)

    cookie_hash = ph.hash(cookie_validator + users_ip)

    # Save cookie to DB
    Cookie.create(user_id=users_id, created=datetime.now(), expires=datetime.now() + timedelta(days=30), cookie_token=cookie_token, cookie_hash=cookie_hash)

    return cookie_token + "." + cookie_validator

def check_cookie():
    cookie_token = request.cookies.get('loggedin')

    if cookie_token is not None:
        cookie_details = cookie_token.split('.')

        cookie = Cookie.get_or_none(Cookie.cookie_token == cookie_details[0])
        if cookie is None:
            return False

        # Check cookie expiration 
        if datetime.now() > cookie.expires:
            return False

        # Validate cookie
        try:
            ph.verify(cookie.cookie_hash, cookie_details[1] + request.remote_addr)
            # To-do, invalidate cookie if the hash verification fails
        except:
            # Cookie invalid
            return False

        return cookie
    else:
        return False

def destroy_cookie():
    try:
        current_cookie = check_cookie()
        current_cookie.delete_instance()
    except:
        # Cookie already deleted
        print("Cookie already deleted")

    return True

def user_from_cookie(cookie):
    if cookie is None:
        # No cookie
        return None

    current_user = User.get(User.users_id == cookie.user_id)
    return dict(username=current_user.username, user_id=current_user.users_id, role=current_user.role)