from flask import Flask
import sass
import os
from dotenv import load_dotenv
from flask_cors import CORS
from pages.home import home
from pages.auth import auth
from pages.error import error
from pages.dash import dash
from pages.logout import logout

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET')

CORS(app)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(error)
app.register_blueprint(dash)
app.register_blueprint(logout)

@app.context_processor
def app_version():
    return dict(version=os.getenv('VERSION'))

sass.compile(dirname=('styles', 'static/styles'))



# from blueprints import register_blueprints  # Auto-register function
# register_blueprints(app)  # Automatically registers all Blueprints