from flask import Blueprint, current_app, redirect, url_for, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.auth import authenticate

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

blueprint = Blueprint('dash', __name__, template_folder='templates', url_prefix='/dash')

blueprint.register_blueprint(spaces)
blueprint.register_blueprint(invites)
blueprint.register_blueprint(files)
blueprint.register_blueprint(links)
blueprint.register_blueprint(keys)

@blueprint.route("/")
@limiter.limit("2/second")
@authenticate
def handle_dash():
    if g.current_user == None:
        return redirect(url_for('home.index'))
    else:
        return redirect(url_for('dash.links.index'))
