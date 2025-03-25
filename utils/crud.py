import json
from flask import request, send_file, jsonify, g
from pathlib import Path
import shutil
from slugify import slugify
from datetime import timedelta
from utils.auth import check_argon
from utils.general import random_string, allowed_files
from utils.permissions import has_permission

from models import *

UPLOAD_FOLDER = Path.cwd() / 'uploads'

# TEMP START

import os
import base64
from argon2 import PasswordHasher

ph = PasswordHasher()

# To-Do:
# - Return lists of invalid or failed items during multi-deletion and multi-creation or fail whole query
# - Impose limits on multi-deletion and multi-creation
# - Make sure all responses return JSON only
# - Check for duplicated within the same set of list data
# - Allow users to download subdirectories whole
# - Limit key creation to be done only from the site/cookie
# - Uploading file called /tmp/test.txt will write to the root tmp folder on linux
# - Slashes and dots somehow allowed in space names
# - Prevent error pages from printing out full errors (leaks path)
# - Rename is_file to something else (filevalidator for example) and force files to have extensions

# TEMP END

# GENERAL START

def get_json_data():
    if request.data:
        try:
            # Try to get JSON from request
            return request.get_json()

        except Exception as e:
            # Invalid request. Error parsing JSON.
            return None
    else:
        # No body in request
        return None

def in_userspace(current_user, target, in_space=False):
    username = slugify(current_user['username'])
    
    # Define base directory
    temp_base = Path(UPLOAD_FOLDER) / username
    if in_space:
        temp_base = temp_base / 'space'

    # Resolve base directory
    BASE_DIR = temp_base.resolve()

    # Normalize target path
    target_destination = (temp_base / target).resolve()

    # Ensure target is within base directory
    try:
        target_destination.relative_to(BASE_DIR)
        return True
    except ValueError:
        return False

def is_file(path):
    _, ext = os.path.splitext(path)
    return bool(ext)

# GENERAL END

# KEYS START

def generate_api_key():
    # Generate a secure, URL-safe API key
    raw_token = os.urandom(16)  # 128-bit security
    encoded_token = base64.urlsafe_b64encode(raw_token).decode('utf-8').rstrip('=')
    return encoded_token

def hash_api_key(api_key):
    # Hash the API key with Argon2
    return ph.hash(api_key)

def delete_keys():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete keys
    if not has_permission(g.current_user, "delete:ownKeys"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of keys or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No keys provided."}), 400

    existing_keys = Key.select().where(
        Key.name.in_(json_data) & (Key.owner == g.current_user['user_id'])
    )

    if not existing_keys.exists():
        return jsonify({"success": False, "message": "No keys found."}), 404

    # Merge found keys into a list for fast lookup
    existing_keys_set = {key.name for key in existing_keys}

    # Delete keys in database
    deleted_count = Key.delete().where(Key.name.in_(existing_keys_set)).execute()

    return jsonify(success=True, message=f"{deleted_count} key{'s' if deleted_count != 1 else ''} deleted."), 200


    return dict(success=False, message="Permission denied.")

def create_keys():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create links
    if not has_permission(g.current_user, "create:ownKeys"):
        return dict(success = False, message = "Permission denied."), 403

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of keys or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No links provided."}), 400

    valid_keys = []
    valid_keyvalues = []

    for key in json_data:
        # Item not an object
        if not isinstance(key, dict):
            continue

        # Key does not have a name parameter
        if not "name" in key:
            continue

        expires = None

        # Check if key has an expiry date
        if not "expires" in key or key['expires'] == "":
            # No expiry date, set to infinite
            expires = None
        else:
            # Expiry date exists, check if its in the future
            expires = datetime.strptime(key['expires'], "%Y-%m-%d")

            if expires <= datetime.now():
                # Expiry date not in the future, skip
                continue

        MAX_KEYS = 4

        # Check if a user owns any non expired keys
        key_count = Key.select().where(
            (Key.owner == g.current_user['user_id']) & 
            ((Key.expires.is_null(True)) | (Key.expires > datetime.now()))
        ).count()

        # Check if user can bypass limit
        if not has_permission(g.current_user, "ignore:keyLimit") and key_count > MAX_KEYS:
            return jsonify({"success": False, "message": "You cannot create any more keys."}), 403

        # Generate key
        api_key = generate_api_key()
        hashed_key = hash_api_key(api_key)

        valid_keyvalues.append(dict(name = key['name'], key = api_key))
        valid_keys.append(dict(name = key['name'], value = hashed_key, owner = g.current_user['user_id'], expires = expires))

    existing_keys = Key.select().where(
        Key.name.in_([key['name'] for key in valid_keys]) & (Key.owner == g.current_user['user_id'])
    )

    # Convert existing query objects to a set of refs for fast lookup
    existing_refs = {key.name for key in existing_keys}

    # Filter out valid_links that already exist in the database
    valid_keys = [key for key in valid_keys if key['name'] not in existing_refs]
    valid_keyvalues = [key for key in valid_keyvalues if key['name'] not in existing_refs]

    if not valid_keys:
        return jsonify({"success": False, "message": "Couldn't create keys. Names repeat."}), 400

    Key.insert_many(valid_keys).execute()

    created_count = len(valid_keys)

    return jsonify(success=True, message=f"{created_count} key{'s' if created_count != 1 else ''} created.", keys=valid_keyvalues), 200

# KEYS END

# LINKS START

def get_links():
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Get all links created by user
    own_links = Link.select().where(Link.owner == g.current_user['user_id'])

    # Format links as a JSON array
    links_as_dicts = [
        {key: value for key, value in link.__data__.items() if key not in ['links_id', 'owner']}
        for link in own_links
    ]

    # Return the response
    return jsonify(success = True, links = links_as_dicts), 200

def delete_links():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete links
    if not has_permission(g.current_user, "delete:ownLinks"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of URLs or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No links provided."}), 400

    existing_links = Link.select().where(
        Link.ref.in_(json_data) & (Link.owner == g.current_user['user_id'])
    )

    if not existing_links.exists():
        return jsonify({"success": False, "message": "No links found."}), 404

    # Merge found links into a list for fast lookup
    existing_links_set = {link.ref for link in existing_links}

    # Delete links in database
    deleted_count = Link.delete().where(Link.ref.in_(existing_links_set)).execute()

    return jsonify(success=True, message=f"{deleted_count} link{'s' if deleted_count != 1 else ''} deleted."), 200

def create_links():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create links
    if not has_permission(g.current_user, "create:ownLinks"):
        return dict(success = False, message = "Permission denied."), 403

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of URLs or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No links provided."}), 400

    valid_links = []

    for link in json_data:
        # Item not an object
        if not isinstance(link, dict):
            continue

        # Link does not have a URL parameter
        if not "url" in link:
            continue

        new_alias = None

        # Check if link has alias
        if not "alias" in link or link['alias'] == "":
            new_alias = ''.join(random_string(6))
        else:
            new_alias = link['alias']

        valid_links.append(dict(ref = new_alias, url = link['url'], owner = g.current_user['user_id']))

    existing_links = Link.select().where(
        Link.ref.in_([link['ref'] for link in valid_links])
    )

    # Convert existing query objects to a set of refs for fast lookup
    existing_refs = {link.ref for link in existing_links}

    # Filter out valid_links that already exist in the database
    valid_links = [link for link in valid_links if link['ref'] not in existing_refs]

    if not valid_links:
        return jsonify({"success": False, "message": "Couldn't create links. Aliases already exist."}), 400

    Link.insert_many(valid_links).execute()

    created_count = len(valid_links)

    return jsonify(success=True, message=f"{created_count} link{'s' if created_count != 1 else ''} created."), 200

# LINKS END

# INVITES START

def get_invites():
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Get all invites created by the user
    own_invites = Invite.select().where(Invite.created_by == g.current_user['user_id'])

    # Format invites as a JSON array
    invites_as_dicts = [
        {
            **{key: value for key, value in invite.__data__.items() if key not in ['invites_id', 'created_by']},
            'used_by': invite.used_by.username if invite.used_by else None
        }
        for invite in own_invites
    ]

    # Return the response
    return jsonify(success = True, invites = invites_as_dicts), 200

def delete_invites():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete invites
    if not has_permission(g.current_user, "delete:ownInvites"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of invites or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No invites provided."}), 400

    existing_invites = Invite.select().where(
        Invite.code.in_(json_data) & 
        (Invite.created_by == g.current_user['user_id']) & 
        Invite.used_by.is_null(True)
    )

    if not existing_invites.exists():
        return jsonify({"success": False, "message": "No invites found."}), 404

    # Merge found invites into a list for fast lookup
    existing_invites_set = {invite.code for invite in existing_invites}

    # Delete links in database
    deleted_count = Invite.delete().where(Invite.code.in_(existing_invites_set)).execute()

    return jsonify(success=True, message=f"{deleted_count} invite{'s' if deleted_count != 1 else ''} deleted."), 200

def create_invites():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create invites
    if not has_permission(g.current_user, "create:ownInvites"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    if "count" not in json_data:
        return jsonify({"success": False, "message": "Invalid value in JSON body."}), 400

    # Convert count to int
    count_as_int = 0

    try:
        count_as_int = int(json_data['count'])
    except:
        return jsonify({"success": False, "message": "Invalid value in JSON body."}), 400

    # Check if user cas created 5 invites already
    invite_count = Invite.select().where(Invite.created_by == g.current_user['user_id']).count()

    MAX_INVITES = 5

    # If user has permission, they can create unlimited invites
    if has_permission(g.current_user, "ignore:inviteLimit"):
        remaining_invites = float("inf")  # Unlimited
    else:
        remaining_invites = MAX_INVITES - invite_count  # Calculate how many they can create

    # Check if the requested number exceeds the limit
    if remaining_invites < 1:
        return jsonify({"success": False, "message": "You can not create any more invites."}), 400
    elif count_as_int > remaining_invites:
        return jsonify({"success": False, "message": f"You can only create {remaining_invites} more invite{'s' if remaining_invites != 1 else ''}."}), 400
    
    created_invites = []
    for _ in range(count_as_int):
        created_invites.append(
            dict(
                code = random_string(8),
                expires = datetime.now() + timedelta(days=30),
                created_by = g.current_user['user_id']
            )
        )

    # Make sure the invites are unique
    existing_invites = Invite.select().where(
        Invite.code.in_([invite['code'] for invite in created_invites])
    )

    # Convert existing query objects to a set of refs for fast lookup
    existing_codes = {invite.code for invite in existing_invites}

    # Filter out invites that already exist in the database
    created_invites = [invite for invite in created_invites if invite['code'] not in existing_codes]

    if not created_invites:  # Ensure there's something to insert
        return jsonify({"success": False, "message": "Unknown error."}), 500

    Invite.insert_many(created_invites).execute()

    created_count = len(created_invites)

    return jsonify(success=True, message=f"{created_count} invite{'s' if created_count != 1 else ''} created."), 200

# INVITES END

# FILES START

def get_files():
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Get all links created by user
    own_files = File.select().where(File.owner == g.current_user['user_id'])

    # Format links as a JSON array
    files_as_dicts = [
        {key: value for key, value in file.__data__.items() if key not in ['files_id', 'location', 'owner']}
        for file in own_files
    ]

    # Return the response
    return jsonify(success = True, files = files_as_dicts), 200

def delete_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete files
    if not has_permission(g.current_user, "delete:ownFiles"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of files or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No files provided."}), 400

    existing_files = File.select().where(
        File.filename.in_(json_data) & (File.owner == g.current_user['user_id'])
    )

    if not existing_files.exists():
        return jsonify({"success": False, "message": "No files found."}), 404

    # Merge found files into a list for fast lookup
    existing_files_set = {file.filename for file in existing_files}

    # List to store file paths that will be deleted
    files_to_delete = [Path(UPLOAD_FOLDER) / file.location for file in existing_files]

    # Try to delete files on disk and handle possible errors
    for file_path in files_to_delete:
        try:
            # Check if the file exists and is a valid file
            if file_path.exists() and file_path.is_file():
                file_path.unlink()  # Delete the file
                print(f"Deleted: {file_path}")
            else:
                print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error deleting {file_path}: {e}")

    # Delete files in database
    deleted_count = File.delete().where(File.filename.in_(existing_files_set)).execute()

    return jsonify(success=True, message=f"{deleted_count} file{'s' if deleted_count != 1 else ''} deleted."), 200

def upload_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create files
    if not has_permission(g.current_user, "create:ownFiles"):
        return dict(success = False, message = "Permission denied."), 403

    # Check if the request has files in it
    if 'file' not in request.files:
        return dict(success = False, message="No files found."), 400

    # Get files from request
    files = request.files.getlist('file')

    # Convert username to slug
    username_as_slug = slugify(g.current_user['username'])

    # Make a directory for a user if none exist
    UPLOAD_FOLDER.joinpath(username_as_slug).mkdir(parents=True, exist_ok=True)

    file_records = []

    for file in files:
        filename = file.filename

        # Check if file is allowed
        if not allowed_files(filename):
            continue

        # Generate new random filename
        file_slug = random_string(8)
        new_filename = file_slug + "." + filename.rsplit('.', 1)[1].lower()

        # Get new destination
        file_dest = Path(UPLOAD_FOLDER) / username_as_slug / new_filename

        # Save the file
        file.save(file_dest)

        # Save for DB query
        relative_path = Path(username_as_slug) / new_filename

        file_records.append({
            "owner": g.current_user['user_id'],
            "filename": file_slug,
            "location": str(relative_path),
            "original": filename
        })

    if not file_records:
        # No files passed the filter
        return dict(success = False, message="No files uploaded."), 400

    # Insert created files into DB
    File.insert_many(file_records).execute()

    uploaded_count = len(file_records)

    return jsonify(success=True, message=f"{uploaded_count} file{'s' if uploaded_count != 1 else ''} uploaded."), 200

# FILES END

# SPACES START

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

    return listing

def get_spaces():
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Get all spaces created by user
    own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

    # Format spaces as a JSON array
    spaces_as_dicts = [
        {key: value for key, value in space.__data__.items() if key not in ['spaces_id', 'owner']}
        for space in own_spaces
    ]

    # Return the response
    return jsonify(success = True, spaces = spaces_as_dicts), 200

def delete_spaces():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete spaces
    if not has_permission(g.current_user, "delete:ownSpaces"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of spaces or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No spaces provided."}), 400

    existing_spaces = Space.select().where((Space.owner == g.current_user['user_id']))

    if not existing_spaces.exists():
        return jsonify({"success": False, "message": "No spaces found."}), 404

    # Merge found spaces into a list for fast lookup
    existing_spaces_set = {space.name for space in existing_spaces}

    # Delete spaces on disk
    for space in existing_spaces:
        dir_path = Path(UPLOAD_FOLDER) / g.current_user['username'] / 'space'  # Convert to Path object

        if dir_path.exists() and dir_path.is_dir():
            shutil.rmtree(dir_path)  # Delete directory and all contents
            print(f"Deleted directory: {dir_path}")
        else:
            print(f"The directory {dir_path} does not exist or is not a directory.")

    # Delete spaces in database
    deleted_count = Space.delete().where(Space.name.in_(existing_spaces_set)).execute()

    deleted_count = 1

    return jsonify(success=True, message=f"{deleted_count} space{'s' if deleted_count != 1 else ''} deleted."), 200

def create_spaces():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create spaces
    if not has_permission(g.current_user, "create:ownSpaces"):
        return dict(success = False, message = "Permission denied."), 403 

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of URLs or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No spaces provided."}), 400

    # Check if user cas created a space already
    space_count = Space.select().where(Space.owner == g.current_user['user_id']).count()

    MAX_SPACES = 1

    # If user has permission, they can create unlimited invites
    if has_permission(g.current_user, "ignore:spaceLimit"):
        remaining_spaces = float("inf")  # Unlimited
    else:
        remaining_spaces = MAX_SPACES - space_count  # Calculate how many they can create

    # Check if the requested number exceeds the limit
    if remaining_spaces < 1:
        return jsonify({"success": False, "message": "You can not create any more spaces."}), 400
    elif len(json_data) > remaining_spaces:
        return jsonify({"success": False, "message": f"You can only create {remaining_spaces} more invite{'s' if remaining_spaces != 1 else ''}."}), 400

    # Get name blacklist
    name_blacklist = None
    with open('utils/usernames.json') as f:
        usernames_as_json = json.load(f)
        name_blacklist = usernames_as_json['usernames']

    # Get existing usernames
    existing_usernames = [
        user.username for user in User.select(User.username).where(User.users_id != g.current_user['user_id'])
    ]

    valid_spaces = []

    for space in json_data:
        new_name = slugify(space)

        if new_name in name_blacklist or new_name in existing_usernames:
            # Space name does not pass name filter
            continue

        valid_spaces.append(dict(name = new_name, owner = g.current_user['user_id']))

    existing_spaces = Space.select().where(
        Space.name.in_([space['name'] for space in valid_spaces])
    )

    # Convert existing query objects to a set of refs for fast lookup
    existing_refs = {space.name for space in existing_spaces}

    # Filter out valid_links that already exist in the database
    valid_spaces = [space for space in valid_spaces if space['name'] not in existing_refs]

    if not valid_spaces:
        return jsonify({"success": False, "message": "Couldn't create spaces. Aliases are invalid."}), 400

    # Create a 'space' directory for a user if it doesn't exist
    users_space_directory = Path(UPLOAD_FOLDER) / g.current_user['username'] / 'space'
    users_space_directory.mkdir(parents=True, exist_ok=True)

    # Add created spaces to database
    Space.insert_many(valid_spaces).execute()

    created_count = len(valid_spaces)

    return jsonify(success=True, message=f"{created_count} space{'s' if created_count != 1 else ''} created."), 200

def get_space_files():
    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

    if not own_spaces.exists():
        return jsonify({"success": False, "message": "No spaces found."}), 404

    space_files = None

    working_dir = Path(UPLOAD_FOLDER) / g.current_user['username'] / 'space'
    
    get_tree = space_file_tree(working_dir)

    return jsonify(success=True, files=get_tree), 200

def delete_space_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can delete files
    if not has_permission(g.current_user, "delete:ownFiles"):
        return dict(success = False, message = "Permission denied."), 403 

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

    if not own_spaces.exists():
        return jsonify({"success": False, "message": "No spaces found."}), 404

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of files or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No files or directories provided."}), 400

    deleted_count = 0

    for file in json_data:
        # Check if file destination is in users space
        dest_in_userspace = in_userspace(g.current_user, file, True)

        if not dest_in_userspace:
            continue

        file_path = Path(UPLOAD_FOLDER) / g.current_user['username'] / 'space' / file

        if file_path.exists():
            # Path exists
            if file_path.is_file():
                file_path.unlink()  # Deletes the file
            elif file_path.is_dir():
                shutil.rmtree(file_path)  # Deletes the directory and its contents

            deleted_count += 1
        else:
            # Path does not exist
            continue

    if deleted_count < 1:
        return jsonify({"success": False, "message": "Invalid request. No files or directories were deleted."}), 400

    return jsonify(success=True, message=f"{deleted_count} file{'s' if deleted_count != 1 else ''} deleted."), 200

def upload_space_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create files
    if not has_permission(g.current_user, "create:ownFiles"):
        return dict(success = False, message = "Permission denied."), 403

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

    if not own_spaces.exists():
        return jsonify({"success": False, "message": "No spaces found."}), 404

    # Get files from request
    files = request.files.getlist('file')

    # Convert username to slug
    username_as_slug = slugify(g.current_user['username'])

    uploaded_count = 0

    for file in files:
        new_filename = file.filename

        # User is uploading their space directory
        if new_filename.startswith("space/"):
            new_filename = new_filename[6:]  # 6 is the length of "space/"

        # Check if file is allowed
        if not allowed_files(new_filename):
            continue

        # Check if file destination is in users space
        dest_in_userspace = in_userspace(g.current_user, new_filename, True)
        if not dest_in_userspace:
            continue

        # Get new destination
        file_dest = Path(UPLOAD_FOLDER) / username_as_slug / 'space' / new_filename

        # Ensure the parent directories exist
        file_dest.parent.mkdir(parents=True, exist_ok=True)

        # Save the file
        file.save(file_dest)

        uploaded_count += 1

    if uploaded_count < 1:
        return jsonify({"success": False, "message": "Invalid request. No files or directories were uploaded."}), 400

    return jsonify(success=True, message=f"{uploaded_count} file{'s' if uploaded_count != 1 else ''} uploaded."), 200

def create_space_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    # Check if the user can create files
    if not has_permission(g.current_user, "create:ownFiles"):
        return dict(success = False, message = "Permission denied."), 403

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    # JSON is not a list of URLs or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No filenames provided."}), 400

    # Convert username to slug
    username_as_slug = slugify(g.current_user['username'])

    uploaded_count = 0

    for file in json_data:
        # Check if file destination is in users space
        dest_in_userspace = in_userspace(g.current_user, file, True)
        if not dest_in_userspace:
            continue

        # Get new destination
        file_dest = Path(UPLOAD_FOLDER) / username_as_slug / 'space' / file

        # Ensure the parent directories exist (should also create all directories)
        file_dest.parent.mkdir(parents=True, exist_ok=True)

        if is_file(file):
            # Path is a file

            # Check if file is allowed
            if not allowed_files(file):
                continue

            # Save the file
            if not file_dest.exists():
                try:
                    file_dest.touch()
                except:
                    continue 

                uploaded_count += 1
        else:
            # Path is a directory

            # Check if directory was created successfully
            if file_dest.parent.exists() and file_dest.parent.is_dir():
                uploaded_count += 1

    if uploaded_count < 1:
        return jsonify({"success": False, "message": "Invalid request. No files or directories were created."}), 400

    return jsonify(success=True, message=f"{uploaded_count} file{'s' if uploaded_count != 1 else ''} or director{'ies' if uploaded_count != 1 else 'y'} created."), 200

def download_space_files():
    # Check if the user exists
    if g.current_user is None:
        return dict(success = False, message = "Unauthorized."), 403

    json_data = get_json_data()
    if json_data is None:
        return jsonify({"success": False, "message": "Invalid request. Error parsing JSON body."}), 400

    print(json_data)

    # Retrieve the spaces created by user
    own_spaces = Space.select().where(Space.owner == g.current_user['user_id'])

    if not own_spaces.exists():
        return jsonify({"success": False, "message": "No spaces found."}), 404

    # JSON is not a list of files or is empty
    if not isinstance(json_data, list) or len(json_data) < 1:
        return jsonify({"success": False, "message": "Invalid request. No files provided."}), 400

    # Convert username to slug
    username_as_slug = slugify(g.current_user['username'])

    if len(json_data) > 1:
        # Download as zip here...
        return jsonify(success=False, message="Multi-downloads not implemented yet."), 400
    else:
        # Download single file here
        file = json_data[0]

        # Cant download directory as a single file
        if not is_file(file):
            return jsonify({"success": False, "message": "Invalid request."}), 400

        # Check if file destination is in users space
        dest_in_userspace = in_userspace(g.current_user, file, True)
        if not dest_in_userspace:
            return jsonify({"success": False, "message": "Invalid request."}), 400

        # Get new destination
        file_dest = Path(UPLOAD_FOLDER) / username_as_slug / 'space' / file

        # Check if file exssts
        if not file_dest.exists():
            return jsonify({"success": False, "message": "File doesn't exist."}), 404

        # Send file to user
        return send_file(file_dest, as_attachment=True)

# SPACES END

# puffin, jon and noah were here on 03/23/2025

def check_invite():
    if 'invite' in request.form:
        # Check db for invite
        invite = Invite.get_or_none(Invite.code == request.form['invite'])
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
