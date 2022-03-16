from os import environ

class Config(object):
    SECRET_KEY = environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = environ.get('UPLOAD_FOLDER') or '/tmp'
    LOG_VERBOSITY = environ.get('LOG_VERBOSITY') or 'DEBUG'
    HOST_ADDR = environ.get('HOST_ADDR') or '127.0.0.1'
    BASIC_AUTH_PASSWORD = environ.get('ADMIN_PASSWORD') or 'p@$$w0rd'
    CURRENT_FILE = 'TBD'
    DEBUG_TB_INTERCEPT_REDIRECTS = False
