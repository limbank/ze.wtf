from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import random
import string

ALLOWED_EXTENSIONS = {
    'webp',
    'tiff',
    'png',
    'jpg',
    'jpeg',
    'gif',
    'html',
    'css',
    'json',
    'js',
    'txt',
    'mp3',
    '.mov',
    'mp4',
    'avi',
    'flac',
    'ogg',
    'wav',
    'webm',
    'zip',
    'rar',
    'md',
    "woff",
    "woff2",
    "otf",
    "ttf",
    "svg",
    "ico"
}
# To-Do: make separate list for space-specific file extensions

ph = PasswordHasher()

def check_argon(chash, value):
    try:
        return ph.verify(chash, value)
    except VerifyMismatchError:
        return False

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS