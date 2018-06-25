from flask import Flask
from config import Config
from flask_bootstrap import Bootstrap
from lxml import etree
from bs4 import BeautifulSoup

app = Flask(__name__)
app.static_folder = 'static'
app.config.from_object(Config)

# # For Docker
# app.config['UPLOAD_FOLDER'] = '/home/ohscribe/data'
# app.config['UPLOAD_ALIAS'] = '~/Projects/Docker/OHScribe/data'

# For PyCharm development
app.config['UPLOAD_FOLDER'] = '/Users/markmcfate/data'
app.config['UPLOAD_ALIAS'] = '/Users/markmcfate/data'

bootstrap = Bootstrap(app)

from app import routes, errors, actions

