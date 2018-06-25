from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, FileField, RadioField
from wtforms.validators import DataRequired, Regexp

class MainForm(FlaskForm):
    browse = FileField('Browse', validators=[DataRequired()])
    actions = RadioField('Action', choices=[('cleanup','Clean-Up'), ('transform', 'Transform'), ('convert',
      'Convert hh:mm:ss to Seconds'), ('speakers', 'Format Speakers'), ('analyze', 'Analyze'), ('exit', 'Exit')])
    go = SubmitField('Go')
    
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
