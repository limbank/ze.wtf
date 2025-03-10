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
    else:
        return redirect(url_for('dash.dash_links'))


@dash.route("/dash/invites", methods=['GET', 'POST'])
@limiter.limit("2/second")
def dash_invites():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    if request.method == 'POST':
        create_invite(current_user)
        return redirect(url_for('dash.dash_invites'))

    # Retrieve the invites created by user
    invites = Invites.select().join(User, JOIN.LEFT_OUTER, on=(Invites.used_by == User.users_id)).where(Invites.created_by == current_user['user_id'])

    return render_template("dash_invites.html", username=current_user['username'], domain=request.host, invites = invites)

@dash.route("/dash/links")
@limiter.limit("2/second")
def dash_links():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    # Retrieve the URLs created by user
    links = Link.select().where(Link.owner == current_user['user_id'])

    return render_template("dash_links.html", username=current_user['username'], domain=request.host, links = links)

@dash.route("/dash/images")
@limiter.limit("2/second")
def dash_images():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    # Retrieve the images created by user
    images = File.select().where(File.owner == current_user['user_id'])

    return render_template("dash_images.html", username=current_user['username'], domain=request.host, images = images)