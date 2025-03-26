from flask import Blueprint, render_template, current_app, send_file, redirect, url_for, request, make_response, g
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from argon2 import PasswordHasher

from utils.auth import (
    authenticate,
    authenticate_user,
    check_argon,
    check_captcha,
    is_safe_username,
    make_captcha,
    register_user,
)

limiter = Limiter(
    get_remote_address,
    app=current_app,
    default_limits=["1000 per day", "50 per hour"],
    storage_uri="memory://",
)

blueprint = Blueprint('auth', __name__, template_folder='templates')

@blueprint.route('/captcha')
@limiter.limit("2/second")
def dash_captcha():
    data = make_captcha()

    return send_file(data, mimetype='image/png')

@blueprint.route("/auth/")
@limiter.limit("2/second")
@authenticate
def handle_auth():
    if g.current_user == None:
        return redirect(url_for('auth.handle_login'))
    else:
        return redirect(url_for('dash.handle_dash'))


@blueprint.route("/auth/login/", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def handle_login():
    if g.current_user is not None:
        return redirect(url_for('dash.handle_dash'))

    if request.method == 'POST':
        check_auth = authenticate_user()

        if check_auth['success']:
            # User authenticated, set cookie, then redirect...

            response = make_response(redirect(url_for('dash.handle_dash')))
            response.set_cookie('loggedin', check_auth['cookie'], secure=True, httponly=True, samesite='Lax')

            return response
        else:
            return render_template("login.html", msg=check_auth['msg'])

    return render_template("login.html", msg='')

@blueprint.route("/auth/register", methods=['GET', 'POST'])
@limiter.limit("2/second")
@authenticate
def handle_register():
    if g.current_user is not None:
        return redirect(url_for('dash.handle_dash'))

    if request.method == 'POST':
        check_reg = register_user()

        if check_reg['success']:
            # User registered, set cookie, then redirect...

            response = make_response(redirect(url_for('dash.handle_dash')))
            response.set_cookie('loggedin', check_reg['cookie'], secure=True, httponly=True, samesite='Lax')

            return response
        else:
            return render_template("register.html", msg=check_reg['msg'])

    return render_template("register.html", msg='')