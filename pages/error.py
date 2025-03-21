from flask import Blueprint, render_template
from dotenv import load_dotenv
from utils.cookies import check_cookie, user_from_cookie
from werkzeug.exceptions import HTTPException

error = Blueprint('error', __name__, template_folder='templates')

# @error.app_errorhandler(Exception)
# def handle_error(e):
#     # Get token for the header
#     valid_cookie = check_cookie()
#     username = None
#     user_id = None

#     if valid_cookie != False:
#         current_user = user_from_cookie(valid_cookie)
#         username = current_user['username']
#         user_id = current_user['user_id']

#     # Doesn't work for errors on spaces due to the domain being different...

#     code = 500
#     if isinstance(e, HTTPException):
#         code = e.code

#     error_data = dict(code = code, text = str(e))

#     return render_template('error.html', error=error_data, username=username), code