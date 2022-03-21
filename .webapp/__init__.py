# Debugging is per https://stackoverflow.com/questions/17309889/how-to-debug-a-flask-app

import os
import logging
from flask import Flask
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap

## Was previously in config.py
class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp'
    LOG_VERBOSITY = os.environ.get('LOG_VERBOSITY') or 'DEBUG'
    HOST_ADDR = os.environ.get('HOST_ADDR') or '0.0.0.0'  # 127.0.0.1 for DEV, 0.0.0.0 for PROD
    # HOST_ADDR = os.environ.get('MASTER_IP') or '0.0.0.0'
    BASIC_AUTH_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'p@$$w0rd'
    CURRENT_FILE = 'TBD'
    DEBUG_TB_INTERCEPT_REDIRECTS = False


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
app.logger.info('OHScribe "host" = %s.', host)

## Per https://github.com/flask-extensions/Flask-SimpleLogin
# SimpleLogin(app)    ...perhaps it is too simple?

## Per http://flask-basicauth.readthedocs.io/en/latest/
# basic_auth = BasicAuth(app)     ...broken and no longer maintained
# app.config['BASIC_AUTH_USERNAME'] = 'admin'

## Per https://pypi.org/project/flask-htpasswd/
# app.config['FLASK_HTPASSWD_PATH'] = '/Users/mcfatem/.htpasswd'
# app.config['FLASK_SECRET'] = 'Hey Hey Kids, secure me!'
# htpasswd.init_app(app)

# from webapp import simple_routes, errors, actions
# from webapp import routes, errors, actions

# Use the host's IP address per https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network
# Always encapsulate the '.run' call per https://stackoverflow.com/questions/29356224/error-errno-98-address-already-in-use
# if __name__ == '__main__':
#   app.run(host=host, port=5000)