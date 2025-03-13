from flask import Blueprint, render_template, request, redirect, abort, url_for, current_app, send_from_directory
from dotenv import load_dotenv
import validators
import random
import string
import json
from utils.cookies import check_cookie, user_from_cookie

from werkzeug.utils import secure_filename
from pathlib import Path
from slugify import slugify
from datetime import datetime

UPLOAD_FOLDER = Path.cwd() / 'uploads'
ALLOWED_EXTENSIONS = {'webp', 'tiff', 'png', 'jpg', 'jpeg', 'gif'}

# Only import urls here instead
from models import *

home = Blueprint('home', __name__, template_folder='templates')

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def create_link(user_id):
    # Create URL
    url = request.form.get('url')
    url_name = request.form.get('name')
    error = None

    gen_msg = "Not a valid URL! Remember to include the schema."

    if url is None:
        # Form submitted without URL
        return dict(error=gen_msg, url_available=None)

    if not validators.url(url):
        # URL is invalid
        return dict(error=gen_msg, url_available=None)

    # Validate alias if available
    if url_name == "":
        url_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
    else:
        # Check if url alias is allowed
        url_slug = slugify(url_name)

        with open('utils/usernames.json') as f:
            data = json.load(f)
            if url_slug in data['usernames']:
                return dict(error="URL alias not allowed.", url_available=None)

        # Verify alias not existing
        alias_count = Link.select().where(Link.ref == url_slug).count()
        if alias_count > 0:
            return dict(error="URL alias already exists.", url_available=None)

    # Add URL to database
    Link.create(url=url, date_created=datetime.now(), ref=url_slug, owner=user_id)

    return dict(url_available=url_slug, error=None)

def delete_link(slug, user_id):
    short_link = Link.get_or_none(ref=slug)

    if short_link is None:
        return dict(success=False, message="Link does not exist.")

    if short_link.owner != user_id:
        return dict(success=False, message="Permission denied.")
        
    # Delete link
    short_link.delete_instance();

    return dict(success=True, message="Url with the slug " + slug + " has been deleted.")

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
        return redirect(url_for('home.links'))
    else: 
        return render_template("home/index.html")

@home.route("/links", methods=['GET', 'POST'], defaults={'path': ''})
def links(path):
    # Check cookie
    valid_cookie = check_cookie()
    username = None
    user_id = None

    if valid_cookie == False:
        return redirect(url_for('home.index'))
    else:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    if (request.content_type == "application/json"):
        content = request.json
        if 'delete' in content:
            deleted_url = delete_link(content['delete'], user_id)
            return(deleted_url)

    # Prepare return variable default
    new_url = dict(error=None, url_available=None)

    if request.method == 'POST':
        # If a POST request was submitted, create URL
        new_url = create_link(user_id)

    return render_template("home/links.html", error=new_url['error'], url_available = new_url['url_available'], domain=request.host, username=username)

@home.route("/images", methods=['GET', 'POST'], defaults={'path': ''})
def images(path):
    # Check cookie
    valid_cookie = check_cookie()
    username = None
    user_id = None

    if valid_cookie == False:
        return redirect(url_for('home.index'))
    else:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            # No file part
            return dict(success = False, message="File not found.")

        file = request.files['file']

        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            # No selected file
            return dict(success = False, message="File not found.")

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # Convert username to slug
            username_as_slug = slugify(username)
            # Make a directory for a user if none exist
            UPLOAD_FOLDER.joinpath(username_as_slug).mkdir(parents=True, exist_ok=True)

            # Generate new random filename
            file_slug = random_string(8)
            new_filename = file_slug + "." + filename.rsplit('.', 1)[1].lower()
            # Get new destination
            file_dest = Path(UPLOAD_FOLDER) / username_as_slug / new_filename

            # Save file
            file.save(file_dest)

            # Write file to DB
            # To-Do: make sure file name is unique in db without throwing error
            relative_path = Path(username_as_slug) / new_filename
            File.create(owner=user_id, created=datetime.now(), filename=file_slug, location=relative_path, original=filename)

            # Inform user of success
            return dict(success = True, message="Success! Your file is available at: " + request.host + "/" + file_slug)
        else:
            # File not allowed
            print(file.filename)
            print(allowed_file(file.filename))
            return dict(success = False, message="Filetype not allowed.")

    return render_template("home/images.html", domain=request.host, username=username)

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
