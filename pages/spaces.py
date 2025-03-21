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

    # Check if a space exists
    if space_data is None:
        # Maybe redirect to home instead...
        return abort(404)

    # Check if the owner is banned
    if space_data.owner.role == 3:
        return abort(404)

    # Get user's space directory (slugify username)
    named_file_path = Path(user_spaces) / slugify(space_data.owner.username) / "space"
    # Do we need secure_filename for path?

    # To-Do:
    # Figure out whether we should assume .html for unnamed links
    # Return file router when index.html is not present ?

    # Render space
    try:
        # User requested a file
        return send_from_directory(named_file_path, path)
    except:
        # File wasn't found, attempt to fetch subdirectory root
        if not path.endswith(".html"):
            if path == "":
                # User requested directory root
                print("12312")
                return send_from_directory(named_file_path, "index.html")
            else:
                #To-Do: If /blogs isnt found, look for blogs.html first, then index html in /blog/
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
