from flask import Blueprint, render_template, current_app, abort, Response, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import mistune
import os
from utils.general import content_to_rss, get_content, sort_posts
from utils.auth import authenticate
from utils.meta import parse

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

blueprint = Blueprint('changelog', __name__, template_folder='templates/changelog')
    
@blueprint.route('/changelog', defaults={'post': None}, strict_slashes=False)
@blueprint.route("/changelog/<post>", strict_slashes=False)
@limiter.limit("2/second")
@authenticate
def index(post):
    username = None

    if  g.current_user is not None:
        username = g.current_user['username']

    # list all the files in the posts directory
    filenames = get_content()

    if post is None:
        sortedposts = sort_posts(filenames)

        latest = sortedposts.pop()

        return render_template('index.html', posts=sortedposts[::-1], latest=latest, username=username)
    elif post == "feed.xml":
        sortedposts = sort_posts(filenames, False)

        xml = content_to_rss(sortedposts[::-1])

        return Response(xml, mimetype='text/xml')
    elif post in filenames:
        with open("./changelog/" + post + ".md", "r") as f:
            file_content = f.read()

        file_metadata = parse(file_content)
        post_content = mistune.html(file_metadata[1])

        title = file_metadata[0]['title']
        date = file_metadata[0]['date']
        ver = file_metadata[0].get('version', None)

        return render_template('single.html', postdata=post_content, p_title=title, date=date, ver=ver, username=username)
    else:
        abort(404)
