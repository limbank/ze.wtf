from flask import Blueprint, render_template, current_app, redirect, url_for, request, after_this_request, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.permissions import has_permission
from utils.auth import authenticate
from pathlib import Path
from utils.crud import (
    get_spaces,
    delete_spaces,
    create_spaces,
    get_space_files,
    delete_space_files,
    upload_space_files,
    create_space_files,
    download_space_files,
    get_space_archive,
    create_temp_zip,
)

from models import Space

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

spaces = Blueprint('spaces', __name__, template_folder='templates')

@spaces.route("/spaces/", methods=['GET', 'POST'], defaults={'path': ''})
@spaces.route("/spaces/<string:path>", methods=['GET', 'POST'])
@spaces.route("/spaces/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def index(path):
    # Handle requests for the API
    if request.method == 'POST':
        if path == "create" and request.content_type == "application/json":
            created_spaces = create_spaces()
            return created_spaces
        elif path == "delete" and request.content_type == "application/json":
            deleted_spaces = delete_spaces()
            return deleted_spaces

        return dict(success = False, message = "Invalid request."), 400

    elif request.method == 'GET' and request.content_type == "application/json":
        if path is None or path == "":
            # Get spaces
            user_spaces = get_spaces()
            return user_spaces
        else:
            return dict(success = False, message = "Invalid request."), 400

    # Handle non-JSON requests

    # Clean up path if its used wrong
    if path != "":
        return redirect(url_for('dash.spaces.index'))

    if g.current_user == None:
        # User unauthenticated, return to homepage
        return redirect(url_for('home.index'))
    else:
        # Retrieve the spaces created by user
        own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

        # Retreive space-related permissions for user
        can_delete = has_permission(g.current_user, "delete:ownSpaces")

        return render_template("dash/spaces.html", username=g.current_user['username'], domain=request.host, spaces = own_spaces, can_delete = can_delete)

@spaces.route("/spaces/files/", methods=['GET', 'POST'], defaults={'path': ''})
@spaces.route("/spaces/files/<string:path>", methods=['GET', 'POST'])
@spaces.route("/spaces/files/<path:path>", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def files(path):
    if g.current_user == None:
        # User unauthenticated
        return dict(success = False, message = "Unauthorized."), 403

    # Handle requests for the API
    if request.method == 'POST':
        if path == "upload" and request.content_type.startswith("multipart/form-data"):
            # Multipart here
            uploaded_files = upload_space_files()
            return uploaded_files
        elif path == "delete" and request.content_type == "application/json":
            deleted_files = delete_space_files()
            return deleted_files
        elif path == "create" and request.content_type == "application/json":
            created_files = create_space_files()
            return created_files
        elif path == "download" and request.content_type == "application/json":
            space_file = download_space_files()
            return space_file

        return dict(success = False, message = "Invalid request."), 400

    elif request.method == 'GET' and request.content_type == "application/json":
        if path is None or path == "":
            space_files = get_space_files()
            return space_files
        elif path == "archive" and request.content_type == "application/json":
            zip_path = create_temp_zip()
            space_archive = get_space_archive(zip_path)

            #Ensure ZIP is deleted after request is processed
            @after_this_request
            def cleanup(response):
                try:
                    Path(zip_path).unlink(missing_ok=True)  # Delete the temporary ZIP file
                except Exception as e:
                    print(f"Failed to delete temp ZIP: {e}")
                return response

            return space_archive
        else:
            return dict(success = False, message = "Invalid request."), 400

    # Handle non-JSON requests
    return redirect(url_for('dash.spaces.index'))
