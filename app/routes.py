from flask import render_template, flash, redirect, url_for, request
from app import app
from app.forms import MainForm
from app.actions import do_cleanup, do_transform


@app.route('/')
@app.route('/main', methods=['POST', 'GET'])
def main():
  form = MainForm()
  if form.validate_on_submit():
    flash("Form submitted with file '{}'".format(form.browse.data), 'info')
    return redirect(url_for('results'))
  return render_template('main.html', title='Controls', form=form)


@app.route('/results', methods=['POST', 'GET'])
def results():

  result = request.form
  filename = str(result['browse'])
  flash("The selected file (result['browse']) is: '{}'.".format(filename), 'info')
  action = str(result['actions'])
  flash("You selected the '{}' action.".format(action), 'info')

  # Take action here...
  if action == "cleanup":
    msg = do_cleanup(filename)
  elif action == "transform":
    msg = do_transform(filename)
 
  return render_template("results.html", result=result, message=msg)
