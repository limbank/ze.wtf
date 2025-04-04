from flask import Blueprint, current_app, render_template, current_app
from flask_limiter import Limiter
import time
from pathlib import Path
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

blueprint = Blueprint('nerds', __name__, template_folder='templates')

intervals = (
    ('weeks', 604800),  # 60 * 60 * 24 * 7
    ('days', 86400),    # 60 * 60 * 24
    ('hours', 3600),    # 60 * 60
    ('minutes', 60),
    ('seconds', 1),
)

def display_time(seconds, granularity=2):
    result = []

    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            if value == 1:
                name = name.rstrip('s')
            result.append("{} {}".format(value, name))
    return ', '.join(result[:granularity])

def get_directory_size(path='.'):
    """Returns the total size of the directory in a human-readable format."""
    path = Path(path)
    total_size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())

    # Dynamically format the size
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if total_size < 1024:
            return f"{total_size:.2f} {unit}"
        total_size /= 1024

    return f"{total_size:.2f} TB"  # Fallback in case it's massive

@blueprint.route("/nerds")
@limiter.limit("2/minute")
def index():
    valid_cookie = check_cookie()
    username = None
    user_id = None
    if valid_cookie != False:
        # Get user if logged in
        current_user = user_from_cookie(valid_cookie)
        username = current_user['username']
        user_id = current_user['user_id']

    start_time = current_app.config.get('START_TIME', time.time())  # Get start time
    uptime_seconds = time.time() - start_time
    project_size = get_directory_size()

    link_count = Link.select().count()
    user_count = User.select().count()
    file_count = File.select().count()
    invite_count = Invite.select().count()
    space_count = Space.select().count()

    appinfo = dict(
        test="hello",
        uptime=display_time(uptime_seconds),
        size=project_size,
        links=link_count,
        users=user_count,
        files=file_count,
        invites=invite_count,
        spaces=space_count
    )

    return render_template("nerds.html", data=appinfo, username=username)
