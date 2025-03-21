import validators
import json
from flask import request, send_file
from pathlib import Path
import shutil
from slugify import slugify
from datetime import datetime, timedelta
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

def delete_file(slug, current_user):
    user_id = current_user['user_id']

    selected_file = File.get_or_none(filename=slug)

    if selected_file is None:
        return dict(success=False, message="Image does not exist.")

    if selected_file.owner != user_id or not has_permission(current_user, "delete:ownFiles"):
        return dict(success=False, message="Permission denied.")

    # Check if image exists, if it does, delete it on disk
    file_path = Path.cwd() / 'uploads' / selected_file.location
    if file_path.is_file():
        file_path.unlink()
    else:
        return dict(success=False, message="Image does not exist.")

    # Delete image in DB
    selected_file.delete_instance();

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
        url_name = slugify(url_name)

        with open('utils/usernames.json') as f:
            data = json.load(f)
            if url_name in data['usernames']:
                return dict(error="URL alias not allowed.", url_available=None)

    # Verify alias not existing
    alias_count = Link.select().where(Link.ref == url_name).count()
    if alias_count > 0:
        return dict(error="URL alias already exists.", url_available=None)

    # Add URL to database
    Link.create(url=url, date_created=datetime.now(), ref=url_name, owner=user_id)

    return dict(url_available=url_name, error=None)

def create_file(current_user):
    # To-Do: fix duplication and multiple files at once
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
        print(allowed_files(file.filename))
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

def upload_space_files(current_user):
    username = current_user['username']
    user_id = current_user['user_id']

    # Capture JSON here TEMPORARILY

    # Check if the content is sent in JSON
    if (request.content_type == "application/json"):
        single_space_file = get_space_file(current_user)
        return single_space_file

    destination = request.form.get('destination')
    entire_dir = request.form.get('entire-dir')
    dirname = request.form.get('dirname')

    # Check if the user can create files
    can_create = has_permission(current_user, "create:ownFiles")
    if not can_create:
        return dict(success = False, message = "Missing permission.")


    if entire_dir is not None:
        print("Uploading whole dir")
        # check if the post request has the file part
        if 'file' not in request.files:
            # No file part
            return dict(success = False, message="No files found.")

        # Prevent file creation if the user is not allowed to
        if not has_permission(current_user, "create:ownFiles"):
            return dict(success=False, message="Permission denied.")

        files = request.files.getlist('file')

        root_folder = None  # To track the first directory (root)

        for file in files:
            # Check if file is allowed
            if not allowed_files(file.filename):
                continue

            # Determine the root directory (first part before '/')
            if root_folder is None:
                root_folder = file.filename.split('/')[0]  # Extract the first directory

            # Strip the root folder from the path
            relative_path = Path(file.filename).relative_to(root_folder)

            # Convert username to slug
            username_as_slug = slugify(username)

            # Get new destination
            file_dest = Path.cwd() / 'uploads' / username_as_slug / 'space' / relative_path

            # Define the trusted base directory
            temp_base = Path.cwd() / 'uploads' / username_as_slug / 'space'
            BASE_DIR = Path(temp_base).resolve()

            # Resolve new path
            temp_path = Path(file_dest).resolve()

            # Check new path against basedir
            if BASE_DIR not in temp_path.parents:
                return dict(success = False, message = "File or directory incorrect")

            # Ensure the parent directory exists before saving
            file_dest.parent.mkdir(parents=True, exist_ok=True)

            # Save the file
            file.save(file_dest)

        # Rebuild file tree
        return get_space_files(current_user)

    # User is uploading a file
    if dirname is None:
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

            # Get new destination
            file_dest = Path(UPLOAD_FOLDER) / username_as_slug / 'space' / destination / filename

            # Define the trusted base directory
            temp_base = Path.cwd() / 'uploads' / username_as_slug / 'space'
            BASE_DIR = Path(temp_base).resolve()

            # Resolve new path
            temp_path = Path(file_dest).resolve()

            # Check new path against basedir
            if BASE_DIR not in temp_path.parents:
                return dict(success = False, message = "File or directory does not exist")

            # Save file
            #print("Will write...")
            #print(file_dest)

            file.save(file_dest)

            # Rebuild file tree
            return get_space_files(current_user)
        else:
            # File not allowed
            print(file.filename)
            print(allowed_files(file.filename))
            return dict(success = False, message="Filetype not allowed.")

    # User is creating a directory
    if dirname is not None:
        target_dir = Path.cwd() / 'uploads' / slugify(username) / 'space' / destination / slugify(dirname)

        # Define the trusted base directory
        temp_base = Path.cwd() / 'uploads' / slugify(username) / 'space'
        BASE_DIR = Path(temp_base).resolve()

        # Resolve new path
        temp_path = Path(target_dir).resolve()

        # Check new path against basedir
        if BASE_DIR not in temp_path.parents:
            return dict(success = False, message = "File or directory does not exist")

        # Create directory
        target_dir.mkdir()

        # Rebuild file tree
        return get_space_files(current_user)

def space_file_tree(working_dir):
    base_path = working_dir  # This is the root path for the listing
    p = Path(working_dir).glob('**/*')

    # Prepare lists
    directories = []
    files = []

    for path in p:
        relative_path = path.relative_to(base_path).as_posix()  # Make it relative & use forward slashes
        if path.is_dir():
            directories.append(relative_path + '/')  # Add trailing slash for directories
        else:
            files.append(relative_path)

    # Sort them (directories first, then files)
    directories.sort()
    files.sort()

    # Combine into a JSON-serializable format
    listing = {
        "directories": directories,
        "files": files
    }

    # Convert to JSON
    space_files = json.dumps(listing)
    return space_files

def get_space_files(current_user):
    user_id = current_user['user_id']

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == user_id)

    space_files = None

    if own_spaces is not None:
        working_dir = Path.cwd() / 'uploads' / current_user['username'] / 'space'
        
        return space_file_tree(working_dir)

    return dict(success = False, message = "Incomplete")

def get_space_file(current_user):
    username = current_user['username']
    user_id = current_user['user_id']

    if (request.content_type != "application/json"):
        return dict(success = False, message = "Malformed request")

    content = request.json

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == user_id)

    if own_spaces.count() == 0:
        return dict(success = False, message = "You do not have a space")

    # Check if the user can edit files
    can_delete = has_permission(current_user, "edit:ownFiles")
    if not can_delete:
        return dict(success = False, message = "Missing permission.")

    space_file = content['edit']

    #print("Our file?")
    #print(space_file)

    #To-Do: filter which files can be edited

    # Create new directory path
    target_file = Path.cwd() / 'uploads' / slugify(username) / 'space' / space_file

    #print("testing....")
    #print(Path.cwd() / 'uploads' / slugify(username) / 'space')
    # Define the trusted base directory
    temp_base = Path.cwd() / 'uploads' / slugify(username) / 'space'
    BASE_DIR = Path(temp_base).resolve()

    #print("Our target?")
    #print(target_file)

    # Resolve new path
    temp_path = Path(target_file).resolve()

    #print("Our path?")
    #print(temp_path)

    # Check new path against basedir
    if BASE_DIR not in temp_path.parents:
        return dict(success = False, message = "File or directory does not exist")

    # Check if file exists
    if target_file.exists():
        if target_file.is_file():
            # Return the file contents
            return send_file(target_file, as_attachment=True)

    return dict(success = False, message = "Error editing file")

def delete_space_files(current_user):
    user_id = current_user['user_id']
    username = current_user['username']

    # Check if the content is sent in JSON
    if (request.content_type != "application/json"):
        return dict(success = False, message = "Malformed request")

    content = request.json

    # Check if the content contains file name
    if 'delete' not in content:
        return dict(success = False, message = "Name invalid")

    # Check if the user can delete files
    can_delete = has_permission(current_user, "delete:ownFiles")
    if not can_delete:
        return dict(success = False, message = "Missing permission.")

    # Check if users space exists
    users_spaces = Space.select().where(Space.owner == user_id).count()
    if users_spaces < 1:
        return dict(success = False, message = "You do not have a space")

    # Create new directory path
    target_file = Path.cwd() / 'uploads' / slugify(username) / 'space' / content['delete']

    # Define the trusted base directory
    temp_base = Path.cwd() / 'uploads' / slugify(username) / 'space'
    BASE_DIR = Path(temp_base).resolve()

    # Resolve new path
    temp_path = Path(target_file).resolve()

    # Check new path against basedir
    if BASE_DIR not in temp_path.parents:
        return dict(success = False, message = "File or directory does not exist")

    # Check if file exists
    if target_file.exists():
        if target_file.is_file():
            #print("will unlink")
            target_file.unlink()  # Deletes the file
        elif target_file.is_dir():
            #print("will rmtree")
            shutil.rmtree(target_file)  # Deletes the directory and its contents

        # return the new file tree here
        #print(f"{target_file} has been deleted.")
        return get_space_files(current_user)
    else:
        return dict(success = False, message = "File or directory does not exist")
    
    # Delete file

    return dict(success = True, message = "Deleted file")

def create_space(current_user):
    user_id = current_user['user_id']
    username = current_user['username']

    # Check if the content is sent in JSON
    if (request.content_type != "application/json"):
        return dict(success = False, message = "Malformed request")

    content = request.json

    # Check if the content contains space name
    if 'name' not in content:
        return dict(success = False, message = "Name invalid")

    # Check if the user can create spaces
    can_create = has_permission(current_user, "create:ownSpaces")
    if not can_create:
        return dict(success = False, message = "Missing permission.")

    # Check if user already has a space
    users_spaces = Space.select().where(Space.owner == user_id).count()
    if users_spaces > 0:
        return dict(Success = False, message = "You can only create one space")

    new_name = slugify(content['name'])

    # Check if name is allowed
    with open('utils/usernames.json') as f:
        data = json.load(f)
        if new_name in data['usernames']:
            return dict(success = False, message="Name not allowed")

    # Check if name is a username and doesnt belong to current user
    user_count = User.select().where(((User.username == content['name']) | (User.username == new_name)) & (User.users_id != user_id)).count()
    if user_count > 0:
        return dict(success = False, message = "Name already exists")

    # Check if space name exists
    space_count = Space.select().where(Space.name == new_name).count()
    if space_count > 0:
        return dict(success = False, message = "Name already exists")

    # Create space
    created_space = Space.create(name=new_name, owner=user_id)

    # Make a space directory in users folder
    new_space_dir = Path.cwd() / 'uploads' / slugify(username) / 'space'
    new_space_dir.mkdir()

    return dict(success = True, message = "Space created. Give us a second...")

def check_invite():
    if 'invite' in request.form:
        # Check db for invite
        invite = Invites.get_or_none(Invites.code == request.form['invite'])
        if invite is None:
            # Invite does not exist
            return dict(msg = "You need a valid invite to join!", success = False)

        if invite.used_by is not None:
            # Invite already used
            return dict(msg = "Invite has already been used!", success = False)

        if datetime.now() > invite.expires:
            # Invite already expired
            return dict(msg = "Invite has expired!", success = False)

        return dict(msg = "Invite valid!", success = True)
    else:
        return dict(msg = "Missing invite code", success = False)

def create_invite(current_user):
    # Check if the content is sent in JSON
    if (request.content_type != "application/json"):
        return dict(success = False, message = "Malformed request")

    content = request.json

    if current_user is None:
        return dict(success = False, message = "Unauthorized.")

    # Check if user cas created 5 invites already
    invite_count = Invites.select().where(Invites.created_by == current_user['user_id']).count()

    # Check if user can add aliases ?

    # Check if user is banned
    if current_user['role'] == 3:
        return dict(success = False, message = "You cannot create any more invites.")

    # Check if user can bypass limit
    if not has_permission(current_user, "ignore:inviteLimit") and invite_count > 4:
        return dict(success = False, message = "You cannot create any more invites.")

    invite_code = random_string(8)

    # Check if the content contains an alias
    if 'create' in content and content['create'] != "":
        invite_code = slugify(content['create'])

    # Create invite
    Invites.create(created_by=current_user['user_id'], expires=datetime.now() + timedelta(days=30), code=invite_code)

    return dict(success = True, message = "Invite created")

