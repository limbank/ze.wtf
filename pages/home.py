from flask import Blueprint, render_template, request, redirect, abort
from dotenv import load_dotenv
import validators
import random
import string
from utils.cookies import check_cookie, user_from_cookie

# Only import urls here instead
from models import *

home = Blueprint('home', __name__, template_folder='templates')

@home.route("/", methods=['GET', 'POST'], defaults={'path': ''})
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

    url = request.form.get('url')
    error = None

    # extractor = URLExtract()
    # urls = extractor.find_urls(url)
    # print(len(urls))

    if url is not None:
        print("URL NOT NONE")
        print(url)
        if not validators.url(url):
            error = "\"" + url + "\" is not a valid URL! Remember to include the schema."
        else:
            newID = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
            print(newID)
            Link.create(url=url, ref=newID, owner=user_id)
            error = "New URL available at " + request.host + "/" + newID
            print("Done!")

    return render_template("home.html", error=error, domain=request.host, username=username)

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
