from flask import Flask, render_template, flash, redirect, url_for, request
from app import app
from app.forms import MainForm, LoginForm
from app.actions import do_cleanup, do_transform, do_hms_conversion, do_speaker_tags, do_analyze, do_all, \
  upload_to_server
import sys


# Route for handling the login page logic
@app.route('/', methods=['POST', 'GET'])
@app.route('/login', methods=['POST', 'GET'])
def login():
  form = LoginForm(request.form)
  if request.method == 'POST':
    if (form.username.data == "admin" and form.password.data == "Grinn311C0113g3"):
      flash("Login permitted for user '{}'".format(form.username.data))
      return redirect(url_for('main'))
    else:
      flash("Authentication failed.  Please try again or contact digital@grinnell.edu for proper credentials.", 'error')
      return redirect(url_for('login'))
  return render_template('login.html', title='Sign In', form=form)


# Route for handling the main/control page
@app.route('/main', methods=['POST', 'GET'])
def main():
  form = MainForm(request.form)
  if request.method == 'POST':
    return redirect(url_for('results'))
  return render_template('main.html', title='Controls', form=form)


# Route for handling the results page
@app.route('/results', methods=['POST', 'GET'])
def results():
  result = request.form
  method = request.method

  try:
    result['exit']
  except:
    pass
  else:
    exit(0)

  filename = str(result['browse'])
  if filename:
    uploaded = upload_to_server(filename)
  else:
    flash("For any Action you must select a file to process.  Try again or 'Exit'?", 'error')
    return redirect(url_for('main'))
  
  try:
    result['all']
  except:
    pass
  else:
    file, msg, details, guidance = do_all(filename)
    return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  try:
    if result['action'] and result['go']:
      action = str(result['actions'])
      if action == "cleanup":
        file, msg, details, guidance = do_cleanup(filename)
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "transform":
        file, msg, details, guidance = do_transform(filename)
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "convert":
        file, msg, details, guidance = do_hms_conversion(filename)
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "speakers":
        file, msg, details, guidance = do_speaker_tags(filename)
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "analyze":
        file, msg, details, guidance = do_analyze(filename)
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  except IsADirectoryError:
    flash("Directory selected.  Use the 'Browse' button in the Main / Control Screen to select a file for "
          "processing.", 'error')
    return redirect(url_for('main'))

  except TypeError:
    flash("No file selected.  Use the 'Browse' button in the Main / Control Screen to select a file for processing.",
      'error')
    return redirect(url_for('main'))

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))
  

