from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.invites import create_invite
from utils.permissions import has_permission
from utils.crud import delete_invite, delete_image
from pathlib import Path

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

    if (request.content_type == "application/json"):
        content = request.json
        if 'delete' in content:
            deleted_invite = delete_invite(content['delete'], current_user)
            return(deleted_invite)

    if request.method == 'POST':
        create_invite(current_user)
        return redirect(url_for('dash.dash_invites'))

    # Retrieve the invites created by user
    invites = Invites.select().join(User, JOIN.LEFT_OUTER, on=(Invites.used_by == User.users_id)).where(Invites.created_by == current_user['user_id'])

    # Retreive invite-related permissions for user
    can_delete = has_permission(current_user, "delete:ownInvites")
    can_create = has_permission(current_user, "create:ownInvites")

    return render_template("dash/invites.html", username=current_user['username'], domain=request.host, invites = invites, can_delete = can_delete, can_create=can_create)

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

    # Retreive link-related permissions for user
    can_delete = has_permission(current_user, "delete:ownLinks")

    return render_template("dash/links.html", username=current_user['username'], domain=request.host, links = links, can_delete = can_delete)

@dash.route("/dash/images", methods=['GET', 'POST'])
@limiter.limit("2/second")
def dash_images():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    if (request.content_type == "application/json"):
        content = request.json
        if 'delete' in content:
            deleted_image = delete_image(content['delete'], current_user)
            return(deleted_image)

    # Retrieve the images created by user
    images = File.select().where(File.owner == current_user['user_id'])

    # Retreive image-related permissions for user
    can_delete = has_permission(current_user, "delete:ownFiles")

    return render_template("dash/images.html", username=current_user['username'], domain=request.host, images = images, can_delete = can_delete)