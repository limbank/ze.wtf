from flask import Blueprint, render_template, current_app, redirect, url_for, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.permissions import has_permission
from utils.crud import get_links, create_links, delete_links, latest_blot
from utils.auth import authenticate
from models import Link

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

links = Blueprint('links', __name__, template_folder='templates')

@links.route("/links/", methods=['GET', 'POST'], defaults={'path': ''})
@links.route("/links/<string:path>", methods=['GET', 'POST'])
@links.route("/links/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def index(path):
    # Handle JSON requests for the API
    if request.method == 'POST' and request.content_type == "application/json":
        if path == "create":
            created_links = create_links()
            return created_links
        elif path == "delete":
            deleted_links = delete_links()
            return deleted_links

        return dict(success = False, message = "Invalid request"), 400

    elif request.method == 'GET' and request.content_type == "application/json":
        if path is None or path == "":
            # Get links
            user_links = get_links()
            return user_links
        else:
            return dict(success = False, message = "Invalid request."), 400

    # Handle non-JSON requests

    # Clean up path if its used wrong
    if path != "":
        return redirect(url_for('dash.links.index'))

    # Authenticate user
    if g.current_user == None:
        # User unauthenticated, return to homepage
        return redirect(url_for('home.index'))
    else:
        # User authenticated, proceed

        # Retrieve the URLs created by user
        own_links = Link.select().where(Link.owner == g.current_user['user_id'])

        # Retreive link-related permissions for user
        can_delete = has_permission(g.current_user, "delete:ownLinks")

        # Get latest blotter post
        blot = latest_blot()

        # Render dashboard page
        return render_template("dash/links.html", username=g.current_user['username'], domain=request.host, links = own_links, can_delete = can_delete, blot = blot)
