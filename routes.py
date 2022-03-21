from ohscribe import app
from flask import render_template, flash, redirect, url_for, request, send_file
from forms import MainForm
from actions import do_cleanup, do_transform, do_hms_conversion, do_speaker_tags, do_analyze, do_all, allowed_file
from werkzeug.utils import secure_filename
import sys
import os

# ## From https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# @app.route('/')
# @app.route('/index')
# def index():
#     return "Hello, World!"

## Line below was subordinate to `@app.route('/upload', methods=['GET', 'POST'])`
# @basic_auth.required  # per http://flask-basicauth.readthedocs.io/en/latest/

## Route for handing authentication and upload selection
# @app.route('/login', methods=['POST', 'GET'])
# @app.route('/logout', methods=['POST', 'GET'])

@app.route('/upload', methods=['GET', 'POST'])
# @htpasswd.required
def upload_file():
  app.logger.debug("upload_file( ) called")

  if request.method == 'POST':

    # Check if the post request has the file part
    if 'file' not in request.files:
      flash('No file part', 'error')
      return redirect(request.url)

    file = request.files['file']

    # If user does not select file, browser also submit an empty part without filename
    if file.filename == '':
      flash('No selected file', 'error')
      return redirect(request.url)

    # Good to go...
    if file and allowed_file(file.filename):
      filename = secure_filename(file.filename)

      folder = app.config['UPLOAD_FOLDER']
      app.logger.debug("folder at line 47 in .simple_routes.py is: '%s'", folder)
      newpath = os.path.join(folder, filename)
      app.logger.debug("newpath at line 49 in .simple_routes.py is: '%s'", newpath)

      try:
        file.save(newpath)
        flash("Your file has been successfully uploaded to {}".format(newpath), 'info')
        app.config['CURRENT_FILE'] = newpath
        app.logger.info("Uploaded file is: %s", newpath)
        return redirect(url_for('main'))
      except:
        msg = "Upload error. Make sure you have a 'data' folder under 'ohscribe' and that it is open for the world to write files."
        flash(msg, 'error')
        raise
#      except:
#        msg = "Unexpected error: {}".format(sys.exc_info()[0])
#        flash(msg, 'error')
#        raise

  return render_template('upload.html', title='Upload XML File')


# # Route for displaying the uploaded file
# @app.route('/uploads/<filename>')
# def CURRENT_FILE(filename):
#     return send_from_directory(os.environ.get('OHSCRIBE_UPLOAD_FOLDER'), filename)

# Route for handling download section
@app.route('/download')
def download_file( ):
  target = app.config['CURRENT_FILE']
  app.logger.info("Target output for download is: %s", target)
  dir, filename = os.path.split(target)
  return send_file(target, mimetype='text/xml', cache_timeout=0, attachment_filename=filename, as_attachment=True)

# Route for handling the main/control page
@app.route('/', methods=['POST', 'GET'])
@app.route('/main', methods=['POST', 'GET'])
def main( ):
  form = MainForm(request.form)
  if request.method == 'POST':
    return redirect(url_for('results'))
  return render_template('main.html', title='Controls', form=form)


# Route for handling the results page
@app.route('/results', methods=['POST', 'GET'])
def results( ):
  result = request.form
  method = request.method

  try:
    result['exit']
  except:
    pass
  else:
    exit(0)

  filename = app.config['CURRENT_FILE']

  try:
    result['all']
  except:
    pass
  else:
    file, msg, details, guidance = do_all(filename)
    app.config['CURRENT_FILE'] = file
    return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  try:
    if result['actions'] and result['go']:
      action = str(result['actions'])
      if action == "cleanup":
        file, msg, details, guidance = do_cleanup(filename)
        app.config['CURRENT_FILE'] = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "transform":
        file, msg, details, guidance = do_transform(filename)
        app.config['CURRENT_FILE'] = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "convert":
        file, msg, details, guidance = do_hms_conversion(filename)
        app.config['CURRENT_FILE'] = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "speakers":
        file, msg, details, guidance = do_speaker_tags(filename)
        app.config['CURRENT_FILE'] = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "analyze":
        file, msg, details, guidance = do_analyze(filename)
        app.config['CURRENT_FILE'] = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))
