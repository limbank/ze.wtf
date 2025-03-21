from flask import Blueprint, render_template, current_app, redirect, url_for, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from utils.cookies import check_cookie, user_from_cookie
from utils.permissions import has_permission
from utils.crud import delete_file, upload_files

from models import *

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

files = Blueprint('files', __name__, template_folder='templates')

@files.route("/files", methods=['GET', 'POST'])
@limiter.limit("2/second")
def index():
    # Check cookie
    valid_cookie = check_cookie()

    if valid_cookie == False:
        return redirect(url_for('home.index'))

    current_user = user_from_cookie(valid_cookie)

    if (request.content_type == "application/json"):
        content = request.json
        if 'delete' in content:
            deleted_file = delete_file(content['delete'], current_user)
            return(deleted_file)

    if request.method == 'POST':
        uploaded_files = upload_files(current_user)
        return uploaded_files

    # Retrieve the files created by user
    files = File.select().where(File.owner == current_user['user_id'])

    # Retreive image-related permissions for user
    can_delete = has_permission(current_user, "delete:ownFiles")

    return render_template("dash/files.html", username=current_user['username'], domain=request.host, files = files, can_delete = can_delete)