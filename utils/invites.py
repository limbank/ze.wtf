from flask import  request
from datetime import datetime, timedelta
import random
import string
from models import *

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

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
    else:
        return dict(msg = "Missing invite code", success = False)

def create_invite(current_user):
    if current_user is not None:
        # Check if user cas created 5 invites already
        invite_count = Invites.select().where(Invites.created_by == current_user['user_id']).count()

        if invite_count < 5:
            # Create invite
            invite_code = random_string(8)
            # Is this necessary?
            user = User.get_or_none(User.users_id == current_user['user_id'])
            Invites.create(created_by=user, created=datetime.now(), expires=datetime.now() + timedelta(days=30), code=invite_code)

    return "hi"
