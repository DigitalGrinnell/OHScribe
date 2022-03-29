# OHScribe! Development History

## Move to Reclaim Cloud

In March 2022 a move was made to migrate the __OHScribe!__ application to a new host, [Reclaim Cloud](https://reclaim.cloud/) (RC).  A few changes were required to get the code working properly in RC's version of a `wsgi` production environment.  Intended functionality remains unchanged, as does most of the layout, theme, and behavior.

### Necessary Changes for Reclaim Cloud

_Reclaim Cloud_ employs a [Jelastic](https://jelastic.com/) interface for PaaS configuration.  There's helpful documentation in one of Jelastic's blog posts, [Python Cloud Hosting with Jelastic Paas](https://jelastic.com/blog/python-cloud-hosting/), but it lacks anything specific to [Flask](https://flask.palletsprojects.com/en/2.1.x/) or the [Web Server Gateway Interface](https://en.wikipedia.org/wiki/Web_Server_Gateway_Interface) (WSGI) production server that RC provides.

There are many flavors of WSGI and subsequently many ways to configure it. I found the official Flask documentation at https://flask.palletsprojects.com/en/2.0.x/deploying/ to be most helpful.  However, that documentation presents 6 different techniques for working with 6 different cloud providers like _Heroku_, _Google_, _AWS_, _Azure_, and _PythonAnywhere_.  I tried all 6, and as luck would have it, the _last of the six_ worked.  _Jelastic_ is not mentioned in any of this documentation (not that I could find anyway), but if you follow the _PythonAnywhere_ example it works!

Ultimately I found the documents at https://help.pythonanywhere.com/pages/Flask/ to be most helpful.

### `wsgi.py` Holds the Key

To successfully run a Python/Flask app in a _Jelastic_/WSGI environment I found it necessary to create a new `wsgi.py` file, and mine reads like this:

```wsgi.py
## Per https://help.pythonanywhere.com/pages/Flask/

import sys
path = '/var/www/webroot/ROOT'
if path not in sys.path:
   sys.path.insert(0, path)

from ohscribe import app as application
```

I also merged all of my previously "distributed" code (copies are now found in files named `.obsolete/routes.py`, `.obsolete/forms.py`, `.obsolete,errors.py`, `.obsolete/actions.py`, and `app.py`) into a single source code file named `ohscribe.py`.  This move wasn't entirely necessary but it does make path-handling easier in the production environment.

The critical portions of `ohscribe.py` that correspond with `wsgi.py` read like this:

```ohscirbe.py
# Initialize the app... populate app.config[] and session[] keys
app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
```

...and...

```ohscribe.py
if __name__ == '__main__':    # development?  Returns false in production, I think.
    app.run()
```

### Implement `Session` from `flask_session`

The final necessary change required that I engage the `flask_session` library and make use of a web `Session` to persist user selections and data from one operation to the next.  See `ohscribe.py` for additional details.

| Attention! |
| --- |
| Most of what follows is **obsolete**, replaced by the features and deployment details outlined above. |

## Early History

**OHScribe!** was developed to replace my old **Transform_InqScribe_to_IOH** (https://github.com/DigitalGrinnell/Transform_InqScribe_to_IOH) application, hereto abbreviated as *TIIOH*.  *TIIOH* is a Python 2 desktop application with lots of obscure dependencies. It was described as...

```
This is a Python 2 script, with GUI, designed to transform oral history transcripts, presumably created using InqScribe, into XML suitable for ingest into the Islandora Oral Histories (IOH) Solution Pack to populate a TRANSCRIPT datastream and its derivatives.
```

*TIIOH* used the Python *Tk* and *Tkinter* libraries to provide its graphical user interface, and as such the application was suitable for use only as an installed app in an OSX or Linux desktop environment.  In 2018 a few users working in Windows outside the Grinnell College campus were identified it quickly became evident that a more 'portable' solution was needed.  

A decision was made to 'Dockerize' the application for cross-platform compatability but that was extremely difficult to do with *Tk* and *Tkinter* involved.  Subsequently, it was decided that *TIIOH* should be a web-based application so that it could be used from any suitable platform with a web browser, and that decision prompted a move to Python 3 and Flask, still in a 'Dockerized' form.

**OHScribe!** was eventually developed from a short-lived project I called **SPADE** - *Single Page Application in a Desktop Environment*.  What follows is largely a discussion about **SPADE**.


# SPADE - Single Page Application in a Desktop Environment

This Flask tutorial app is based on work found in
https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world.  I built this Dockerized iteration of _SPADE_ by working through Chapters 1, 2, and 3, then borrowing from elements of Chapters 11 and 19.  

Form and results handling was also influenced by https://www.tutorialspoint.com/flask/flask_sending_form_data_to_template.htm.

CSS clues were found in https://stackoverflow.com/questions/34664156/flask-bootstrap-custom-theme.  

Form field specs can be found at http://wtforms.readthedocs.io/en/latest/fields.html and field validators at http://wtforms.readthedocs.io/en/latest/validators.html.


## Find and Replace

```
microblog -> spade  
Microblog -> SPADE  
login -> main   # renaming the 'login' page/form to 'main', where everything happens
LoginForm -> MainForm
index -> main   # giving 'main' the focus instead of 'index'   
```

Also, be sure to rename `microblog.py` to `spade.py`, and comment out (or remove) the `app.route('/index')` section of `routes.py`.  Delete `index.html`.

## Building the Docker Image
From the `SPADE` folder where `Dockerfile` is found...
```
docker build -t spade:latest .
```

## Launching the Application
From the `SPADE` folder where `Dockerfile` is found...
```
docker run --name spade -d -p 8000:5000 --rm spade:latest
```
You can check that the app is running using `docker ps` which should return something like this:
```
ma8660:SPADE markmcfate$ docker ps
CONTAINER ID        IMAGE                                  COMMAND                  CREATED              STATUS              PORTS                                      NAMES
8f75555f7203        spade:latest                           "./boot.sh"              About a minute ago   Up About a minute   0.0.0.0:8000->5000/tcp                     spade
```

When properly setup you can combine operations like so...  
```
docker-destroy-spade; docker build -t spade:latest .; docker run --name spade -d -p 8000:5000 --rm spade:latest
```

__To interact with the app visit `http://localhost:8000` in your browser.__

## Debugging
In OSX you can check the Docker logs via...
```
tail -100 ~/Library/Containers/com.docker.docker/Data/com.docker.driver.amd64-linux/console-ring
```
