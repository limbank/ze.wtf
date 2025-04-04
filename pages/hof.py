from flask import Blueprint, current_app, render_template, current_app, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.auth import authenticate

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

blueprint = Blueprint('hof', __name__, template_folder='templates')

@blueprint.route("/hof")
@limiter.limit("2/minute")
@authenticate
def index():
    username = None
    if g.current_user is not None:
        username = g.current_user

    return render_template("hof.html", username=username)
