from flask import Blueprint, current_app, redirect, url_for, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import destroy_cookie

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

blueprint = Blueprint('logout', __name__, template_folder='templates')

@blueprint.route("/logout")
@limiter.limit("2/second")
def handle_logout():
    # Delete cookie from DB
    destroy_cookie()
    # Destroy cookie
    response = make_response(redirect(url_for('home.index')))
    response.delete_cookie('loggedin')
    # Back to homepage
    return response
