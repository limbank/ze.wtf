from flask import Blueprint, render_template, current_app, redirect, url_for, make_response, abort
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import destroy_cookie
import mistune
from utils.meta import parse
from datetime import datetime as dt
from utils.cookies import check_cookie, user_from_cookie
import os

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

changelog = Blueprint('changelog', __name__, template_folder='templates')

def get_content(path = "./changelog/"):
    filenames = []
    for root, dirs, files in os.walk(path):
        filenames = [f.split('.')[0] for f in files if not f[0] == '.']
    return filenames

def content_to_rss(content):
    rss = f'''<rss version="2.0">
                <channel>
                    <title>{request.host} changelog</title>
                    <link>https://{request.host}/changelog/</link>
                    <description>Changelog</description>
                    <image>
                        <url>https://{request.host}/static/favicon.ico</url>
                        <title>{request.host}</title>
                        <link>https://{request.host}</link>
                    </image>
                    <generator>raccoon butt - raccoonbutt.com</generator>
                    <language>en-us</language>
                    <lastBuildDate>{dt.now().strftime("%B %d, %Y")}</lastBuildDate>'''
    for post in content:
        rss += f'''<item>
                        <title>{post['title']}</title>
                        <link>
                            https://{request.host}/changelog/{post['slug']}
                        </link>
                        <pubDate>{dt.strptime(post['date'], '%m/%d/%Y').date().strftime("%B %d, %Y")}</pubDate>
                        <guid>
                            https://{request.host}/changelog/{post['slug']}
                        </guid>
                        <description><![CDATA[ {post['content']} ]]></description>
                    </item>'''
    rss += '</channel></rss>'
    return rss

def sort_posts(posts, lock=True):
    sorted_posts = []

    for post in posts:
        #To-Do: Change this to absolute path
        with open("./changelog/" + post + ".md", "r") as f:
            file_content = f.read()
        file_metadata = parse(file_content)
        new_date = file_metadata[0]['date']
        new_title = file_metadata[0]['title']
        new_category = file_metadata[0].get("category", None)

        post_content = mistune.html(file_metadata[1])
        preview = post_content.partition("</p>")[0] + "</p>"

        if lock ==  True and (new_category == None or new_category == "general"):
            sorted_posts.append({
                "content": post_content,
                "preview": preview,
                "slug": post,
                "date": new_date,
                "title": new_title
            })
        else:
            sorted_posts.append({
                "content": post_content,
                "preview": preview,
                "slug": post,
                "date": new_date,
                "title": new_title
            })

    #sort by date
    newlist = sorted(sorted_posts, key=lambda d: dt.strptime(d['date'], "%m/%d/%Y"))
    return newlist
    
@changelog.route('/changelog', defaults={'post': None}, strict_slashes=False)
@changelog.route("/changelog/<post>", strict_slashes=False)
@limiter.limit("2/second")
def index(post):
    # Check cookie
    valid_cookie = check_cookie()
    username = None
    user_id = None

    if valid_cookie != False:
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    # list all the files in the posts directory
    filenames = get_content()

    if post is None:
        sortedposts = sort_posts(filenames)

        latest = sortedposts.pop()

        return render_template('changelog.html', posts=sortedposts[::-1], latest=latest, username=username)
    elif post == "feed.xml":
        sortedposts = sort_posts(filenames, False)

        xml = content_to_rss(sortedposts[::-1])

        return Response(xml, mimetype='text/xml')
    elif post in filenames:
        #To-Do: Change this to absolute path
        with open("./changelog/" + post + ".md", "r") as f:
            file_content = f.read()

        file_metadata = parse(file_content)
        post_content = mistune.html(file_metadata[1])

        title = file_metadata[0]['title']
        date = file_metadata[0]['date']

        return render_template('changelog_single.html', postdata=post_content, p_title=title, date=date, username=username)
    else:
        abort(404)
