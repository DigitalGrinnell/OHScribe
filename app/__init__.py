from os import environ
from flask_bootstrap import Bootstrap
from flask import Flask

# Constants/secrets moved to .env, accessed using os.environ below

# Initialize the app... populate app.config[]
app = Flask(__name__)
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = environ.get('UPLOAD_FOLDER')
app.config['SECRET_KEY'] = environ.get('SECRET_KEY')

bootstrap = Bootstrap(app)

from app import routes, errors, actions

# Use the host's IP address per https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network
app.run(host= '0.0.0.0', port=5000)
