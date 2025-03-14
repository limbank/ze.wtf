from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
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

    #return "Test"
    return render_template("dash/spaces.html", username=current_user['username'], domain=request.host, spaces = own_spaces, can_delete = can_delete)