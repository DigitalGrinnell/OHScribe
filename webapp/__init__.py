# Debugging is per https://stackoverflow.com/questions/17309889/how-to-debug-a-flask-app

import os
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
# from config import Config
import config

# Initialize the app... populate app.config[]
app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'

# Set log verbosity based on environment
if app.config['LOG_VERBOSITY'] == 'DEBUG':
  app.debug = True    # for debugging...set False to turn off the DebugToolbarExtension
else:
  app.debug = False   # for debugging...set False to turn off the DebugToolbarExtension

# From The Flask Mega-Tutorial Part VII: Error Handling
if not os.path.exists('logs'):
  os.mkdir('logs')
file_handler = RotatingFileHandler('logs/ohscribe.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
  '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

app.logger.addHandler(file_handler)
file_handler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)

if app.config['LOG_VERBOSITY'] == 'DEBUG':
  file_handler.setLevel(logging.DEBUG)
  app.logger.setLevel(logging.DEBUG)

app.logger.info('OHScribe startup with LOG_VERBOSITY = %s.', app.config['LOG_VERBOSITY'])

bootstrap = Bootstrap(app)
host = app.config['HOST_ADDR']

## Per https://github.com/flask-extensions/Flask-SimpleLogin
# SimpleLogin(app)    ...perhaps it is too simple?

## Per http://flask-basicauth.readthedocs.io/en/latest/
# basic_auth = BasicAuth(app)     ...broken and no longer maintained
# app.config['BASIC_AUTH_USERNAME'] = 'admin'

## Per https://pypi.org/project/flask-htpasswd/
# app.config['FLASK_HTPASSWD_PATH'] = '/Users/mcfatem/.htpasswd'
# app.config['FLASK_SECRET'] = 'Hey Hey Kids, secure me!'
# htpasswd.init_app(app)

# from app import simple_routes, errors, actions
from app import routes, errors, actions

# Use the host's IP address per https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network
# Always encapsulate the '.run' call per https://stackoverflow.com/questions/29356224/error-errno-98-address-already-in-use
if __name__ == '__main__':
  # app.run(host=host, port=5000)    # for PROD host='0.0.0.0' and for DEV host='127.0.0.1'
  app.run(host='0.0.0.0')
