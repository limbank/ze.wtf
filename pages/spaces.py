from flask import Blueprint, render_template, request, redirect, abort, url_for, send_from_directory
from pathlib import Path
from werkzeug.exceptions import NotFound
from models import *

from werkzeug.utils import secure_filename

user_spaces = Path.cwd() / "uploads"

spaces = Blueprint('spaces', __name__, template_folder=user_spaces, subdomain='<subdomain>')

UPLOAD_FOLDER = Path.cwd() / 'uploads'

# @spaces.route("/", subdomain='<subdomain>')
# def index(subdomain):
#     user_template = "salem" + "/space/index.html"
#     return render_template(user_template)

@spaces.route("/", subdomain='<subdomain>', defaults={'path': ''})
@spaces.route("/<string:path>", subdomain='<subdomain>')
@spaces.route('/<path:path>', subdomain='<subdomain>')
def catch_all(path, subdomain):
    # Get user's space direcotry
    named_file_path = Path(user_spaces) / "salem" / "space"
    secure_path = secure_filename(path)

    # Do we need secure_filename?

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
        else:
            print("1")

        # File not found in user space
        abort(404)
