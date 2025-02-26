from flask import Blueprint, render_template, request, redirect, abort
from dotenv import load_dotenv
import validators
import random
import string

from models import *

# user = User.get(User.username == 'admin')
# print(user.date_joined)

#User.create(username='admin')

home = Blueprint('home', __name__, template_folder='templates')

@home.route("/", methods=['GET', 'POST'], defaults={'path': ''})
def index(path):
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
            Link.create(url=url, ref=newID)
            error = "New URL available at /" + newID
            print("Done!")


    return render_template("home.html", error=error)

@home.route("/<string:path>")
@home.route('/<path:path>')
def catch_all(path):
    short_link = Link.get_or_none(ref=path)
    if short_link is not None:
        return redirect(short_link.url)
    else:
        abort(404)


# @home.route('/', defaults={'path': ''})
# @home.route("/<string:path>")
# @home.route('/<path:path>')
# def catch_all(path):
#     return 'You want path: %s' % path