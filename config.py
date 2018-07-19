from os import environ

class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER') or '/tmp'
    CURRENT_FILE = 'TBD'
