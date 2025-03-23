from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.permissions import has_permission
from utils.crud import delete_keys, create_keys, authorize_user
import base64

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

keys = Blueprint('keys', __name__, template_folder='templates')

@keys.route("/keys/", methods=['GET', 'POST'], defaults={'path': ''})
@keys.route("/keys/<string:path>", methods=['GET', 'POST'])
@keys.route("/keys/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
def index(path):
    # Handle requests for the API
    if request.method == 'POST':
        if path == "create" and request.content_type == "application/json":
            created_keys = create_keys()
            return created_keys
        elif path == "delete" and request.content_type == "application/json":
            deleted_keys = delete_keys()
            return deleted_keys

        return dict(success = False, message = "Invalid request1."), 400

    # Handle non-JSON requests

    # Clean up path if its used wrong
    if path != "":
        return redirect(url_for('dash.keys.index'))

    # Authenticate user
    current_user = authorize_user()

    if current_user == None:
        # User unauthenticated, return to homepage
        return redirect(url_for('home.index'))
    else:
        # Retrieve the keys created by user
        own_keys = Key.select().where(Key.owner == current_user['user_id'])

        # Retreive link-related permissions for user
        can_delete = has_permission(current_user, "delete:ownKeys")

        return render_template("dash/keys.html", username=current_user['username'], domain=request.host, keys = own_keys, can_delete = can_delete)
