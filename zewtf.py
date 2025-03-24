from flask import Flask, g
import sass
import os
import time
from dotenv import load_dotenv
from flask_cors import CORS

from pages.home import home
from pages.auth import auth
from pages.error import error
from pages.dash import dash
from pages.logout import logout
from pages.changelog import changelog
from pages.spaces import spaces
from pages.nerds import nerds
from pages.hof import hof

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET')
# First number is megabytes
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000
app.config['SERVER_NAME'] = os.getenv('SERVER_NAME')
app.config['START_TIME'] = time.time()

CORS(app)

@app.context_processor
def app_version():
    return dict(version=os.getenv('VERSION'))

@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(error)
app.register_blueprint(dash)
app.register_blueprint(logout)
app.register_blueprint(changelog)
app.register_blueprint(spaces, subdomain='<subdomain>')
app.register_blueprint(nerds)
app.register_blueprint(hof)

sass.compile(dirname=('styles', 'static/styles'))

# from blueprints import register_blueprints  # Auto-register function
# register_blueprints(app)  # Automatically registers all Blueprints
