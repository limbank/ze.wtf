from flask import Flask, g, request
import sass
import os
import time
from dotenv import load_dotenv
from flask_cors import CORS
from pathlib import Path
import importlib
from utils.general import log_access
from pages.spaces import catch_all

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
@log_access
def before_request():
    g.request_start_time = time.time()
    g.request_time = lambda: "%.5fs" % (time.time() - g.request_start_time)

    # Get the host (domain) from the request
    host = request.host.split(":")[0]  # Strip out port if present
    host = host.split(",")[0]  # Strip out extra host if duplicated by NGINX
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

def register_blueprints(app: Flask, package_name: str, package_path: Path):
    # Dynamically import and register all blueprints in the given package
    for module_path in package_path.glob("*.py"):
        if module_path.name == "__init__.py":
            continue

        module_import_path = f"{package_name}.{module_path.stem}"
        module = importlib.import_module(module_import_path)

        if hasattr(module, "blueprint"):
            app.register_blueprint(module.blueprint)
            print(f"Registered blueprint: {module_import_path}")  # Debugging output
        else:
            print(f"Skipping {module_import_path}: No 'blueprint' found")

# Dynamically load blueprints from the `pages` package
register_blueprints(app, "pages", Path(__file__).parent / "pages")

sass.compile(dirname=('styles', 'static/styles'))
