from flask import Blueprint, render_template, current_app, session, send_file, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher
from captcha.image import ImageCaptcha
import os
import string
import random
from dotenv import load_dotenv

load_dotenv()
ph = PasswordHasher()
limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

def random_string(length = 5):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=int(length)))

def check_argon(chash, value):
    try:
        ph.verify(chash, value)
        return True
    except:
        return False

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/captcha')
@limiter.limit("2/second")
def dash_captcha():
    captcha_string = random_string(os.getenv('CAPTCHA_LENGTH'))
    session['captcha'] = phash = ph.hash((captcha_string).lower() + current_app.secret_key)

    image = ImageCaptcha(fonts=['static/fonts/Manrope-Regular.woff'])
    data = image.generate(captcha_string)

    return send_file(data, mimetype='image/png')

@auth.route("/auth/login", methods=['GET', 'POST'])
@limiter.limit("2/second")
def handle_login():
    return render_template("login.html", version=os.getenv('VERSION'))

@auth.route("/auth/register", methods=['GET', 'POST'])
@limiter.limit("2/second")
def handle_register():
    return render_template("register.html", version=os.getenv('VERSION'))
    
@auth.route("/auth")
@limiter.limit("2/second")
def handle_auth():
    return redirect(url_for('auth.handle_login'))
    #return render_template("auth.html", version=os.getenv('VERSION'))