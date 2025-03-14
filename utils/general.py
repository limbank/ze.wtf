from argon2 import PasswordHasher
import random
import string

ALLOWED_EXTENSIONS = {'webp', 'tiff', 'png', 'jpg', 'jpeg', 'gif'}

ph = PasswordHasher()

def check_argon(chash, value):
    try:
        ph.verify(chash, value)
        return True
    except:
        return False

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS