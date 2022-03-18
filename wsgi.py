# per https://flask.palletsprojects.com/en/2.0.x/deploying/mod_wsgi/

# from app import app as application

activate_this = '/var/www/webroot/ROOT/venv/bin/activate'
with open(activate_this) as file_:
    exec(file_.read(), dict(__file__=activate_this))
