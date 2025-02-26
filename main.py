from flask import Flask
import sass
import os
from pages.home import home
from pages.auth import auth
from pages.error import error
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv('SECRET')

CORS(app)

app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(error)

sass.compile(dirname=('styles', 'static/styles'))
