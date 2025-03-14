from flask import Blueprint, render_template, request, redirect, abort, url_for, send_from_directory
from pathlib import Path
from werkzeug.exceptions import NotFound
from slugify import slugify
from utils.crud import get_space

from models import *

from werkzeug.utils import secure_filename

user_spaces = Path.cwd() / "uploads"

spaces = Blueprint('spaces', __name__, template_folder=user_spaces, subdomain='<subdomain>')

UPLOAD_FOLDER = Path.cwd() / 'uploads'

@spaces.route("/", subdomain='<subdomain>', defaults={'path': ''})
@spaces.route("/<string:path>", subdomain='<subdomain>')
@spaces.route('/<path:path>', subdomain='<subdomain>')
def catch_all(path, subdomain):
    # This request runs for all files, static files included

    space_data = get_space(subdomain)
    #print(f"Space Name: {space_data.name}")
    #print(f"Owner: {space_data.owner.username} (ID: {space_data.owner.role})")

    # Check if a space exists
    if space_data is None:
        # Maybe redirect to home instead...
        return abort(404)

    # Check if the owner is banned
    if space_data.owner.role == 3:
        return abort(404)

    # Get user's space directory (slugify username)
    named_file_path = Path(user_spaces) / slugify(space_data.owner.username) / "space"
    # Do we need secure_filename?
    secure_path = secure_filename(path)

    # To-Do:
    # Figure out whether we should assume .html for unnamed links
    # Return file router when index.html is not present
    # Allow custom 404 pages

    # Render space
    try:
        # User requested a file
        return send_from_directory(named_file_path, secure_path)
    except NotFound as e:
        # File wasn't found, attempt to fetch subdirectory root
        if not secure_path.endswith(".html"):
            if secure_path == "":
                # User requested directory root
                return send_from_directory(named_file_path, "index.html")
            else:
                # User requested subdirectory root
                return send_from_directory(named_file_path, secure_path + "/index.html")

        # File not found in user space
        abort(404)
