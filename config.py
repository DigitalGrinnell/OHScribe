from os import environ

class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER') or '/tmp'
    LOG_VERBOSITY = environ.get('LOG_VERBOSITY') or 'INFO'
    HOST_ADDR = environ.get('HOST_ADDR') or '127.0.0.1'
    ADMIN_PASSWORD = environ.get('OHSCRIBE_ADMIN_PASSWORD')
    LOGGED_IN = False
    CURRENT_FILE = 'TBD'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
