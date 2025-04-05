from flask import Blueprint, abort, send_from_directory, request
from pathlib import Path
from slugify import slugify

from models import *

user_spaces = Path.cwd() / "uploads"

blueprint = Blueprint('spaces', __name__, template_folder=user_spaces)

UPLOAD_FOLDER = Path.cwd() / 'uploads'

def get_space(space_name):
    # Used in pages/spaces.py
    try:
        query = (Space
                 .select(Space, User)
                 .join(User, on=(Space.owner == User.users_id))
                 .where(Space.name == space_name)
                 .get())
        return query
    except Space.DoesNotExist:
        return None 

@blueprint.route("/", defaults={'path': ''})
@blueprint.route("/<string:path>")
@blueprint.route('/<path:path>')
def catch_all(path, subdomain, domain):
    print(f"hai! subdomain {subdomain}, domain {domain}")
    # This request runs for all files, static files included

    space_data = get_space(subdomain)

    # Check if a space exists
    if space_data is None:
        # Maybe redirect to home instead...
        return abort(404)

    # Check if the owner is banned
    if space_data.owner.role == 3:
        return abort(404)

    # Get user's space directory (slugify username)
    named_file_path = Path(user_spaces) / slugify(space_data.owner.username) / "space"

    # Render space
    try:
        # User requested a file
        return send_from_directory(named_file_path, path)
    except:
        # File wasn't found, attempt to fetch subdirectory root
        if not path.endswith(".html"):
            if path == "":
                # User requested directory root
                return send_from_directory(named_file_path, "index.html")
            else:
                target_file = Path.cwd() / 'uploads' / slugify(space_data.owner.username) / 'space' / path

                if target_file.exists():
                    return send_from_directory(named_file_path, path + "/index.html")
                
                pass

        # File not found in user space

        # Check if user has a custom 404 page
        target_file = Path.cwd() / 'uploads' / slugify(space_data.owner.username) / 'space' / '404.html'
        if target_file.exists():
            return send_from_directory(named_file_path, "404.html")
        else:
            # Custom 404 page doesn't exist, draw default
            abort(404)
