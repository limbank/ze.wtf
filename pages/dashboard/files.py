from flask import Blueprint, render_template, current_app, redirect, url_for, request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.permissions import has_permission
from utils.auth import authenticate
from utils.crud import get_files, delete_files, upload_files, latest_blot

from models import File

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

files = Blueprint('files', __name__, template_folder='templates')

@files.route("/files/", methods=['GET', 'POST'], defaults={'path': ''})
@files.route("/files/<string:path>", methods=['GET', 'POST'])
@files.route("/files/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def index(path):
    # Handle requests for the API
    if request.method == 'POST':
        if path == "upload" and request.content_type.startswith("multipart/form-data"):
            # Multipart here
            uploaded_files = upload_files()
            return uploaded_files
        elif path == "delete" and request.content_type == "application/json":
            deleted_files = delete_files()
            return deleted_files

        return dict(success = False, message = "Invalid request."), 400

    elif request.method == 'GET' and request.content_type == "application/json":
        if path is None or path == "":
            # Get files
            user_files = get_files()
            return user_files
        else:
            return dict(success = False, message = "Invalid request."), 400

    # Handle non-JSON requests

    # Clean up path if its used wrong
    if path != "":
        return redirect(url_for('dash.files.index'))

    if g.current_user == None:
        # User unauthenticated, return to homepage
        return redirect(url_for('home.index'))
    else:
        # Retrieve the files created by user
        files = File.select().where(File.owner == g.current_user['user_id'])

        # Retreive image-related permissions for user
        can_delete = has_permission(g.current_user, "delete:ownFiles")

        # Get latest blotter post
        blot = latest_blot()

        return render_template("dash/files.html", username=g.current_user['username'], domain=request.host, files = files, can_delete = can_delete, blot = blot)
