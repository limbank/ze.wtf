from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.invites import create_invite

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

dash = Blueprint('dash', __name__, template_folder='templates')

@dash.route("/dash")
@limiter.limit("2/second")
def handle_dash():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    # Retrieve the URLs created by user
    links = Link.select().where(Link.owner == current_user['user_id'])

    # Retrieve the invites created by user
    # TO-DO make invites show names instead of IDs
    invites = Invites.select().join(User, on=(Invites.used_by == User.users_id)).where(Invites.created_by == current_user['user_id'])

    return render_template("dash.html", username=current_user['username'], domain=request.host, links = links, invites = invites)

@dash.route("/dash/invite")
@limiter.limit("2/second")
def create_invite():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)



    # Redirect back to dash
    return redirect(url_for('dash.handle_dash'))