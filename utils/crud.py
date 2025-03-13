from pathlib import Path
from utils.permissions import has_permission
from models import *

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