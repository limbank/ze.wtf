from flask import Blueprint, render_template
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

error = Blueprint('error', __name__, template_folder='templates')

@error.app_errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return render_template('error.html', error=str(e)), code