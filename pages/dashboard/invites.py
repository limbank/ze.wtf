from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.permissions import has_permission
from utils.crud import authorize_user, get_invites, delete_invites, create_invites

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

invites = Blueprint('invites', __name__, template_folder='templates')

@invites.route("/invites/", methods=['GET', 'POST'], defaults={'path': ''})
@invites.route("/invites/<string:path>", methods=['GET', 'POST'])
@invites.route("/invites/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
def index(path):
    # Handle JSON requests for the API
    if request.method == 'POST' and request.content_type == "application/json":
        if path == "create":
            created_invites = create_invites()
            return created_invites
        elif path == "delete":
            deleted_invites = delete_invites()
            return deleted_invites

        return dict(success = False, message = "Invalid request."), 400

    elif request.method == 'GET' and request.content_type == "application/json":
        if path is None or path == "":
            # Get invites
            user_invites = get_invites()
            return user_invites
        else:
            return dict(success = False, message = "Invalid request."), 400

    # Handle non-JSON requests

    # Clean up path if its used wrong
    if path != "":
        return redirect(url_for('dash.invites.index'))

    # Authenticate user
    current_user = authorize_user()

    if current_user == None:
        # User unauthenticated, return to homepage
        return redirect(url_for('home.index'))
    else:
        # User authenticated, proceed

        # Retrieve the invites created by user
        invites = Invite.select().join(User, JOIN.LEFT_OUTER, on=(Invite.used_by == User.users_id)).where(Invite.created_by == current_user['user_id'])

        # Retreive invite-related permissions for user
        can_delete = has_permission(current_user, "delete:ownInvites")
        can_create = has_permission(current_user, "create:ownInvites")

        # Render dashboard page
        return render_template("dash/invites.html", username=current_user['username'], domain=request.host, invites = invites, can_delete = can_delete, can_create=can_create)
