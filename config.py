import os

class Config(object):
    SECRET_KEY = os.environ.get('OHSCRIBE_SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = os.environ.get('OHSCRIBE_UPLOAD_FOLDER')
    
