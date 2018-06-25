from flask import render_template
from app import app

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('405.html'), 405
