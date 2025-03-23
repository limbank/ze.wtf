from flask import Blueprint, render_template, redirect, abort, url_for, send_from_directory, g
from utils.auth import authenticate
from pathlib import Path
from models import Link, File

UPLOAD_FOLDER = Path.cwd() / 'uploads'

home = Blueprint('home', __name__, template_folder='templates')

@home.route("/", defaults={'path': ''})
@authenticate
def index(path):
    if g.current_user == None:
        return render_template("home/index.html")
    else: 
        return redirect(url_for('dash.handle_dash'))

#If the files are too large
@home.app_errorhandler(413)
def request_entity_too_large(error):
    #return dict(success = False, message="File too large."), 413
    print("Too large raised")
    return dict(success = False, message="File too large.")

@home.route("/<string:path>")
@home.route('/<path:path>')
def catch_all(path):
    # Check if slug is a link
    short_link = Link.get_or_none(ref=path)
    if short_link is not None:
        # Update visits counter
        short_link.visits = short_link.visits + 1
        short_link.save()

        # Redirect user to link
        return redirect(short_link.url)

    # Check if slug is a file
    file = File.get_or_none(filename=path)
    if file is not None:
        # Send file
        # Get absolute file path
        file_location = Path(UPLOAD_FOLDER) / file.location
        # Return file
        return send_from_directory(file_location.parent, file_location.name)

    # Failed to find file or link
    abort(404)
