from flask import request
from datetime import datetime as dt
import random
import string
import os
from utils.meta import parse
import mistune

from models import AccessLog

ALLOWED_EXTENSIONS = {
    'webp',
    'tiff',
    'png',
    'jpg',
    'jpeg',
    'gif',
    'html',
    'css',
    'json',
    'js',
    'txt',
    'mp3',
    '.mov',
    'mp4',
    'avi',
    'flac',
    'ogg',
    'wav',
    'webm',
    'zip',
    'rar',
    'md',
    "woff",
    "woff2",
    "otf",
    "ttf",
    "svg",
    "ico"
}

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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
                    <generator>ze.wtf</generator>
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

def get_content(path = "./changelog/"):
    filenames = []
    for root, dirs, files in os.walk(path):
        filenames = [f.split('.')[0] for f in files if not f[0] == '.']
    return filenames
    
def sort_posts(posts, lock=True):
    sorted_posts = []

    for post in posts:
        with open("./changelog/" + post + ".md", "r") as f:
            file_content = f.read()

        file_metadata = parse(file_content)
        new_date = file_metadata[0]['date']
        new_title = file_metadata[0]['title']
        ver = file_metadata[0].get('version', None)

        post_content = mistune.html(file_metadata[1])
        preview = post_content.partition("</p>")[0] + "</p>"

        sorted_posts.append({
            "content": post_content,
            "preview": preview,
            "slug": post,
            "date": new_date,
            "title": new_title,
            "version": ver
        })

    #sort by date
    newlist = sorted(sorted_posts, key=lambda d: dt.strptime(d['date'], "%m/%d/%Y"))
    return newlist

# Decorator to log access
def log_access(func):
    def wrapper(*args, **kwargs):
        ip_address = request.headers.get('X-Forwarded-For', request.remote_addr).split(',')[0]
        # Skip logging for local addresses
        if ip_address in ['127.0.0.1', 'localhost', '::1']:
            return func(*args, **kwargs)  # Skip logging for local requests
        
        user_agent = request.headers.get('User-Agent')
        route = request.path

        # Get the host (domain) from the request
        domain = request.host

        # Log to the database
        #AccessLog.create(ip_address=ip_address, user_agent=user_agent, route=route, domain=domain)
        
        return func(*args, **kwargs)
    return wrapper