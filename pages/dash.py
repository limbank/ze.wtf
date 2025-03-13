from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.invites import create_invite
from pathlib import Path

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

dash = Blueprint('dash', __name__, template_folder='templates')

def delete_invite(slug, user_id):
    selected_invite = Invites.get_or_none(code=slug)

    if selected_invite is None:
        return dict(success=False, message="Invite does not exist.")

    if selected_invite.created_by.users_id != user_id:
        return dict(success=False, message="Permission denied.")
        
    if selected_invite.used_by is not None:
        return dict(success=False, message="Cannot delete used invites.")

    # To-Do: ensure invites expire faster to prevent scamming
    # Delete invite
    selected_invite.delete_instance();

    return dict(success=True, message="Invite with the slug " + slug + " has been deleted.")

def delete_image(slug, user_id):
    selected_image = File.get_or_none(filename=slug)

    if selected_image is None:
        return dict(success=False, message="Image does not exist.")

    if selected_image.owner != user_id:
        return dict(success=False, message="Permission denied.")

    # Check if image exists, if it does, delete it on disk
    image_file = Path.cwd() / 'uploads' / selected_image.location
    if image_file.is_file():
        image_file.unlink()
    else:
        return dict(success=False, message="Image does not exist.")

    # Delete image in DB
    selected_image.delete_instance();

    return dict(success=True, message="Image with the slug " + slug + " has been deleted.")

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
            deleted_invite = delete_invite(content['delete'], current_user['user_id'])
            return(deleted_invite)

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
            deleted_image = delete_image(content['delete'], current_user['user_id'])
            return(deleted_image)

    # Retrieve the images created by user
    images = File.select().where(File.owner == current_user['user_id'])

    return render_template("dash_images.html", username=current_user['username'], domain=request.host, images = images)