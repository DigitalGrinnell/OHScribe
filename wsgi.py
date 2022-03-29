## Per https://help.pythonanywhere.com/pages/Flask/

import sys
path = '/var/www/webroot/ROOT'
if path not in sys.path:
   sys.path.insert(0, path)

from ohscribe import app as application
