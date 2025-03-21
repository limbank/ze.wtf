from flask import Blueprint, render_template, request, redirect, abort, url_for, send_from_directory
from utils.cookies import check_cookie, user_from_cookie
from utils.general import random_string

from pathlib import Path

# Only import urls here instead
from models import *

UPLOAD_FOLDER = Path.cwd() / 'uploads'

home = Blueprint('home', __name__, template_folder='templates')

@home.route("/", defaults={'path': ''})
def index(path):
    # Check cookie
    valid_cookie = check_cookie()
    username = None
    user_id = None
    if valid_cookie != False:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    if username is not None:
        return redirect(url_for('dash.handle_dash'))
    else: 
        return render_template("home/index.html")

#If the files are too large
@home.app_errorhandler(413)
def request_entity_too_large(error):
    #return dict(success = False, message="File too large."), 413
    # PNG image of Ed Sheeran raises this error for some reason. Multipart encoding bug?
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
