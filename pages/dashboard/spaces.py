from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.crud import create_space, get_space_files, delete_space_files, upload_space_files

from utils.permissions import has_permission

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

    return render_template("dash/spaces.html", username=current_user['username'], domain=request.host, spaces = own_spaces, can_delete = can_delete)

@spaces.route("/spaces/files", methods=['GET', 'POST'])
@limiter.limit("2/second")
def get_files():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    if request.method == 'GET':
        space_files = get_space_files(current_user)

        return space_files
    else:
        upload_file = upload_space_files(current_user)

        return upload_file

@spaces.route("/spaces/files/delete", methods=['POST'])
@limiter.limit("2/second")
def delete_files():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    deleted_files = delete_space_files(current_user)

    return deleted_files

@spaces.route("/spaces/create", methods=['POST'])
@limiter.limit("2/second")
def create():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return dict(success = False, message = "Unauthorized")

    current_user = user_from_cookie(valid_cookie)

    new_space = create_space(current_user)
    
    return new_space

# deleted_invite = delete_invite(content['delete'], current_user)
    #return "Test"
    return dict(success = True, message = "Authorized")