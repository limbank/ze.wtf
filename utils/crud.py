import validators
import json
from flask import request
from pathlib import Path
from slugify import slugify
from datetime import datetime
from werkzeug.utils import secure_filename
from utils.general import random_string, allowed_files
from utils.permissions import has_permission

from models import *

UPLOAD_FOLDER = Path.cwd() / 'uploads'

def delete_invite(slug, current_user):
    user_id = current_user['user_id']

    selected_invite = Invites.get_or_none(code=slug)

    if selected_invite is None:
        return dict(success=False, message="Invite does not exist.")

    if selected_invite.created_by.users_id != user_id or not has_permission(current_user, "delete:ownInvites"):
        return dict(success=False, message="Permission denied.")
        
    if selected_invite.used_by is not None:
        return dict(success=False, message="Cannot delete used invites.")

    # To-Do: ensure invites expire faster to prevent scamming
    # Delete invite
    selected_invite.delete_instance();

    return dict(success=True, message="Invite with the slug " + slug + " has been deleted.")

def delete_image(slug, current_user):
    user_id = current_user['user_id']

    selected_image = File.get_or_none(filename=slug)

    if selected_image is None:
        return dict(success=False, message="Image does not exist.")

    if selected_image.owner != user_id or not has_permission(current_user, "delete:ownFiles"):
        return dict(success=False, message="Permission denied.")

    # Check if image exists, if it does, delete it on disk
    image_file = Path.cwd() / 'uploads' / selected_image.location
    if image_file.is_file():
        image_file.unlink()
    else:
        return dict(success=False, message="Image does not exist.")

    # Delete image in DB
    selected_image.delete_instance();

    return dict(success=True, message="Image with the slug " + slug + " has been deleted.")

def delete_link(slug, current_user):
    user_id = current_user['user_id']

    short_link = Link.get_or_none(ref=slug)

    if short_link is None:
        return dict(success=False, message="Link does not exist.")

    if short_link.owner != user_id or not has_permission(current_user, "delete:ownLinks"):
        return dict(success=False, message="Permission denied.")
        
    # Delete link
    short_link.delete_instance();

    return dict(success=True, message="Url with the slug " + slug + " has been deleted.")

def create_link(current_user):
    username = current_user['username']
    user_id = current_user['user_id']

    # Create URL
    url = request.form.get('url')
    url_name = request.form.get('name')
    error = None

    gen_msg = "Not a valid URL! Remember to include the schema."

    if url is None:
        # Form submitted without URL
        return dict(error=gen_msg, url_available=None)

    if not validators.url(url):
        # URL is invalid
        return dict(error=gen_msg, url_available=None)

    # Prevent link creation if the user is not allowed to
    if not has_permission(current_user, "create:ownLinks"):
        return dict(error="Permission denied.", url_available=None)

    # Validate alias if available
    if url_name == "":
        url_name = ''.join(random_string(6))
    else:
        # Check if url alias is allowed
        url_slug = slugify(url_name)

        with open('utils/usernames.json') as f:
            data = json.load(f)
            if url_slug in data['usernames']:
                return dict(error="URL alias not allowed.", url_available=None)

        # Verify alias not existing
        alias_count = Link.select().where(Link.ref == url_slug).count()
        if alias_count > 0:
            return dict(error="URL alias already exists.", url_available=None)

    # Add URL to database
    Link.create(url=url, date_created=datetime.now(), ref=url_slug, owner=user_id)

    return dict(url_available=url_slug, error=None)

def create_file(current_user):
    username = current_user['username']
    user_id = current_user['user_id']

    # check if the post request has the file part
    if 'file' not in request.files:
        # No file part
        return dict(success = False, message="File not found.")

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty file without a filename.
    if file.filename == '':
        # No selected file
        return dict(success = False, message="File not found.")

    # Prevent file creation if the user is not allowed to
    if not has_permission(current_user, "create:ownFiles"):
        return dict(success=False, message="Permission denied.")

    if file and allowed_files(file.filename):
        filename = secure_filename(file.filename)

        # Convert username to slug
        username_as_slug = slugify(username)
        # Make a directory for a user if none exist
        UPLOAD_FOLDER.joinpath(username_as_slug).mkdir(parents=True, exist_ok=True)

        # Generate new random filename
        file_slug = random_string(8)
        new_filename = file_slug + "." + filename.rsplit('.', 1)[1].lower()
        # Get new destination
        file_dest = Path(UPLOAD_FOLDER) / username_as_slug / new_filename

        # Save file
        file.save(file_dest)

        # Write file to DB
        # To-Do: make sure file name is unique in db without throwing error
        relative_path = Path(username_as_slug) / new_filename
        File.create(owner=user_id, created=datetime.now(), filename=file_slug, location=relative_path, original=filename)

        # Inform user of success
        return dict(success = True, message="Success! Your file is available at: " + request.host + "/" + file_slug)
    else:
        # File not allowed
        print(file.filename)
        print(allowed_file(file.filename))
        return dict(success = False, message="Filetype not allowed.")

def get_space(space_name):
    try:
        query = (Space
                 .select(Space, User)
                 .join(User, on=(Space.owner == User.users_id))
                 .where(Space.name == space_name)
                 .get())
        return query
    except Space.DoesNotExist:
        return None 