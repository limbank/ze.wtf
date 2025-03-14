from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.crud import delete_invite, create_invite
from utils.permissions import has_permission

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

invites = Blueprint('invites', __name__, template_folder='templates')

@invites.route("/invites", methods=['GET', 'POST'])
@limiter.limit("2/second")
def index():
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
        return redirect(url_for('dash.invites.index'))

    # Retrieve the invites created by user
    invites = Invites.select().join(User, JOIN.LEFT_OUTER, on=(Invites.used_by == User.users_id)).where(Invites.created_by == current_user['user_id'])

    # Retreive invite-related permissions for user
    can_delete = has_permission(current_user, "delete:ownInvites")
    can_create = has_permission(current_user, "create:ownInvites")

    return render_template("dash/invites.html", username=current_user['username'], domain=request.host, invites = invites, can_delete = can_delete, can_create=can_create)