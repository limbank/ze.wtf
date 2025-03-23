from flask import Blueprint, current_app, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie
from pathlib import Path

from models import *

from .dashboard.spaces import spaces
from .dashboard.invites import invites
from .dashboard.files import files
from .dashboard.links import links
from .dashboard.keys import keys

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

dash = Blueprint('dash', __name__, template_folder='templates', url_prefix='/dash')

dash.register_blueprint(spaces)
dash.register_blueprint(invites)
dash.register_blueprint(files)
dash.register_blueprint(links)
dash.register_blueprint(keys)

@dash.route("/")
@limiter.limit("2/second")
def handle_dash():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))
    else:
        return redirect(url_for('dash.links.index'))
