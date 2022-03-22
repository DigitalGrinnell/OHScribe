## Per https://help.pythonanywhere.com/pages/Flask/

import sys
path = '/var/www/webroot'
if path not in sys.path:
   sys.path.insert(0, path)

from ohscribe import app as application


# # per https://flask.palletsprojects.com/en/2.0.x/deploying/mod_wsgi/
#
# from webapp import app as application
#
# # activate_this = '/var/www/webroot/ROOT/venv/bin/activate'
# # with open(activate_this) as file_:
# #     exec(file_.read(), dict(__file__=activate_this))

# per https://www.pythonanywhere.com/forums/topic/30131/

# import sys
#
# # add your project directory to the sys.path
# project_home = '/var/www/webroot/ROOT/app/'
# if project_home not in sys.path:
#     sys.path = [project_home] + sys.path
#
# # import flask app but need to call it "application" for WSGI to work
# from webapp import app as application  # noqa