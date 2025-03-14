import random
import string

ALLOWED_EXTENSIONS = {'webp', 'tiff', 'png', 'jpg', 'jpeg', 'gif'}

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def allowed_files(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS