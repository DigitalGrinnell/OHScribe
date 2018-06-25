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
