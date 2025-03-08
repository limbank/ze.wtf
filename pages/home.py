from flask import Blueprint, render_template, request, redirect, abort, url_for
from dotenv import load_dotenv
import validators
import random
import string
import json
from utils.cookies import check_cookie, user_from_cookie

# Only import urls here instead
from models import *

home = Blueprint('home', __name__, template_folder='templates')

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
        with open('utils/usernames.json') as f:
            data = json.load(f)
            if url_name in data['usernames']:
                return dict(error="URL alias not allowed.", url_available=None)

        # Verify alias not existing
        alias_count = Link.select().where(Link.ref == url_name).count()
        if alias_count > 0:
            return dict(error="URL alias already exists.", url_available=None)

    # Add URL to database
    Link.create(url=url, ref=url_name, owner=user_id)

    return dict(url_available=url_name, error=None)

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
        return render_template("home.html")

@home.route("/links", methods=['GET', 'POST'], defaults={'path': ''})
def links(path):
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))
    else:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    # If a POST request was submitted, create URL
    new_url = dict(error=None, url_available=None)
    if request.method == 'POST':
        new_url = create_link(user_id)

    return render_template("links.html", error=new_url['error'], url_available = new_url['url_available'], domain=request.host, username=username)

@home.route("/images", methods=['GET', 'POST'], defaults={'path': ''})
def images(path):
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))
    else:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    return render_template("images.html", domain=request.host, username=username)

@home.route("/<string:path>")
@home.route('/<path:path>')
def catch_all(path):
    short_link = Link.get_or_none(ref=path)
    if short_link is not None:
        # Update visits counter
        short_link.visits = short_link.visits + 1
        short_link.save()

        # Redirect user to link
        return redirect(short_link.url)
    else:
        abort(404)
