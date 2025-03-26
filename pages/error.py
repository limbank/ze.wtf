from flask import Blueprint, render_template
from dotenv import load_dotenv
from utils.auth import authenticate
from werkzeug.exceptions import HTTPException

blueprint = Blueprint('error', __name__, template_folder='templates')

@blueprint.app_errorhandler(Exception)
@authenticate
def handle_error(e):
    username = None

    if  g.current_user is not None:
        username = g.current_user['username']

    # Doesn't work for errors on spaces due to the domain being different...

    code = 500
    if isinstance(e, HTTPException):
        code = e.code

    error_data = dict(code = code, text = str(e))

    return render_template('error.html', error=error_data, username=username), code