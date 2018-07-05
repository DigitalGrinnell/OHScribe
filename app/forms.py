from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, RadioField
from wtforms.validators import DataRequired
from flask_wtf.file import FileField


class MainForm(FlaskForm):
  # browse = FileField('Select an XML File to Upload')
  
  actions = RadioField('Action', choices=[
    ('cleanup','Clean-Up the XML'),
    ('transform', 'Transform XML to IOH'),
    ('convert','Convert hh:mm:ss to Seconds'),
    ('speakers', 'Format Speaker Tags'),
    ('analyze', 'Analyze Cue Times')])
    
  all = SubmitField('Do All of the Above')
  go = SubmitField('Do Single Action')
  exit = SubmitField('Exit')

  
class LoginForm(FlaskForm):
  username = StringField('Username', validators=[DataRequired()])
  password = PasswordField('Password', validators=[DataRequired()])
  # remember_me = BooleanField('Remember Me')
  submit = SubmitField('Sign In')




# exit = SubmitField('Exit')
# transform = SubmitField('Transform')
# convert = SubmitField('Convert hh:mm:ss to Seconds')
# formatSpeakers = SubmitField('Format Speakers')
# string = StringField('This field accepts a string', validators=[DataRequired()])
#     password = PasswordField('This field accepts a password', validators=[DataRequired()])
#     checkbox = BooleanField('This is a checkbox')
#     file1 = FileField('Select any File')
# #   file2 = FileField('Select an XML File', [validators.regexp(u'^[^/\\]\.xml$')])  #
# #   file2 = FileField('Select an XML File', validators=[Regexp(u'^[^/\\]\.xml$')])  #
#     button1 = SubmitField('This is button1')
#     button2 = SubmitField('This is button2')
#     button3 = SubmitField('This is button3')
#     submit = SubmitField('This is the Submit button')
