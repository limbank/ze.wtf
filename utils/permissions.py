from models import *

def has_permission(current_user, perm_name):
    user_role_id = current_user['role']

    query = (Permission
             .select(Permission.name)
             .join(RolePerm)
             .where(RolePerm.role_id == user_role_id))

    # Get a list of permission names
    permissions = [perm.name for perm in query]

    # Check if the permission exists in the list
    return perm_name in permissions

def is_banned(current_user):
    if current_user['role'] == 3:
        return True
    return False

# print(has_permission(current_user, "delete:files"))