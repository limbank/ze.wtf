from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher
from datetime import datetime, timedelta

# Change to only import users later
from models import *

ph = PasswordHasher()
limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

def check_cookie():
    cookie_token = request.cookies.get('loggedin')

    if cookie_token:
        cookie_details = cookie_token.split('.')

        cookie = Cookie.get_or_none(Cookie.cookie_token == cookie_details[0])
        if cookie is None:
            # Cookie not found, redirect to home
            return False

        # Check cookie expiration 
        if datetime.now() > cookie.expires:
            return False

        # Validate cookie
        try:
            ph.verify(cookie.cookie_hash, cookie_details[1] + request.remote_addr)
        except:
            # Cookie invalid
            return False

        return cookie

def user_from_cookie(cookie):
    current_user = User.get(User.users_id == cookie.user_id)
    return dict(username=current_user.username)

dash = Blueprint('dash', __name__, template_folder='templates')

@dash.route("/dash")
@limiter.limit("2/second")
def handle_dash():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    return render_template("dash.html", username=current_user.username)
