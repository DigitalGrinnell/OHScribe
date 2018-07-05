from os import environ
from flask_bootstrap import Bootstrap
from flask import Flask

# Constants/secrets moved to .master.env, accessed using os.environ below

# Initialize the app... populate app.config[]
app = Flask(__name__)
app.static_folder = 'static'
app.config['UPLOAD_FOLDER'] = environ.get('OHSCRIBE_UPLOAD_FOLDER')
app.config['SECRET_KEY'] = environ.get('OHSCRIBE_SECRET_KEY') or 'i-hope-you-never-guess-this'
host = environ.get('OHSCRIBE_HOST_ADDR')

bootstrap = Bootstrap(app)

from app import routes, errors, actions

# Use the host's IP address per https://stackoverflow.com/questions/7023052/configure-flask-dev-server-to-be-visible-across-the-network
# Always encapsulate the '.run' call per https://stackoverflow.com/questions/29356224/error-errno-98-address-already-in-use
if __name__ == '__main__':
  app.run(host=host, port=5000)    # for PROD host='0.0.0.0' and for DEV host='127.0.0.1'
