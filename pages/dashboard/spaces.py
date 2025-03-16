from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.permissions import has_permission
from slugify import slugify
import json

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

spaces = Blueprint('spaces', __name__, template_folder='templates')

@spaces.route("/spaces", methods=['GET', 'POST'])
@limiter.limit("2/second")
def index():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == current_user['user_id'])

    # Retreive space-related permissions for user
    can_delete = has_permission(current_user, "delete:ownSpaces")

    #return "Test"
    return render_template("dash/spaces.html", username=current_user['username'], domain=request.host, spaces = own_spaces, can_delete = can_delete)

@spaces.route("/spaces/create", methods=['POST'])
@limiter.limit("2/second")
def create():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return dict(success = False, message = "Unauthorized")

    current_user = user_from_cookie(valid_cookie)

    user_id = current_user['user_id']

    # Check if the content is sent in JSON
    if (request.content_type == "application/json"):
        content = request.json

        # Check if the content contains space name
        if 'name' not in content:
            return dict(success = False, message = "Name invalid")

        # Check if the user can create spaces
        can_create = has_permission(current_user, "create:ownSpaces")
        if not can_create:
            return dict(success = False, message = "Missing permission.")

        # Check if user already has a space
        users_spaces = Space.select().where(Space.owner == user_id).count()
        if users_spaces > 0:
            return dict(Success = False, message = "You can only create one space")

        new_name = slugify(content['name'])

        # Check if name is allowed
        with open('utils/usernames.json') as f:
            data = json.load(f)
            if new_name in data['usernames']:
                return dict(success = False, message="Name not allowed")

        # Check if name is a username and doesnt belong to current user
        user_count = User.select().where(((User.username == content['name']) | (User.username == new_name)) & (User.id != user_id)).count()
        if user_count > 0:
            return dict(success = False, message = "Name already exists")

        # Check if space name exists
        space_count = Space.select().where(Space.name == new_name).count()
        if space_count > 0:
            return dict(success = False, message = "Name already exists")

        # Create space
        created_space = Space.create(name=new_name, owner=user_id)

        return dict(success = True, message = "Space created. Give us a second...")

    else:
        return dict(success = False, message = "Malformed request")

# deleted_invite = delete_invite(content['delete'], current_user)
    #return "Test"
    return dict(success = True, message = "Authorized")