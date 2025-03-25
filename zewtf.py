from flask import Flask, g, request
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
from pages.spaces import spaces, catch_all
from pages.nerds import nerds
from pages.hof import hof

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET')
# First number is megabytes
app.config['MAX_CONTENT_LENGTH'] = 100 * 1000 * 1000
app.config['START_TIME'] = time.time()

CORS(app)

@app.context_processor
def app_version():
    return dict(version=os.getenv('VERSION'))

@app.before_request
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

    # Get the host (domain) from the request
    host = request.host.split(":")[0]  # Strip out port if present
    host = host.split(",")[0]  # Strip out port if duplicated by NGINX
    main_domain = os.getenv('SERVER_NAME')

    # Check if it's a subdomain of example.com or any other domain
    if host.endswith(f".{main_domain}") or host != main_domain:
        domain = None
        subdomain = None
        # This request runs for all files, static files included
        
        # If the domain is exactly the base domain (example.com)
        if host == main_domain:
            domain = host  # It's the main domain, no subdomain
        # If it's a subdomain of example.com
        elif host.endswith(f".{main_domain}") and host != main_domain:
            subdomain = host.split(f".{main_domain}")[0]  # Get the subdomain part
        else:
            domain = host  # It's a full different domain

        #if domain == "procyonid.local":
        #    subdomain = "salem"

        return catch_all(path=request.path[1:], subdomain=subdomain, domain=domain)  # Call the view function directly

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(error)
app.register_blueprint(dash)
app.register_blueprint(logout)
app.register_blueprint(changelog)
app.register_blueprint(spaces)
app.register_blueprint(nerds)
app.register_blueprint(hof)

sass.compile(dirname=('styles', 'static/styles'))

# from blueprints import register_blueprints  # Auto-register function
# register_blueprints(app)  # Automatically registers all Blueprints
