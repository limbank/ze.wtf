from flask import Blueprint, render_template
from dotenv import load_dotenv
from werkzeug.exceptions import HTTPException

error = Blueprint('error', __name__, template_folder='templates')

# @error.app_errorhandler(Exception)
# def handle_error(e):
#     code = 500
#     if isinstance(e, HTTPException):
#         code = e.code

#     error_data = dict(code = code, text = str(e))

#     return render_template('error.html', error=error_data), code