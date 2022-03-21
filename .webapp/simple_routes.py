from webapp import app

## From https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
@app.route('/')
@app.route('/index')
def index():
    return "Hello, World!"
