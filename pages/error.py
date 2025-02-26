from flask import Blueprint, render_template
import os
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

load_dotenv()

error = Blueprint('error', __name__, template_folder='templates')

@error.app_errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return render_template('error.html', version=os.getenv('VERSION'), error=str(e)), code