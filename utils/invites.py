from flask import  request
from datetime import datetime
import random
import string
from models import *

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