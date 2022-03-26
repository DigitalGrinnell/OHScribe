# Debugging is per https://stackoverflow.com/questions/17309889/how-to-debug-a-flask-app

import os
import logging
from flask import Flask, render_template, request, url_for, flash, redirect, send_file
from logging.handlers import RotatingFileHandler
# from flask_bootstrap import Bootstrap

# adding global variable 'current_file' now that the code is in a single file
current_file = 'TBD'      # the name of the file to be processed next

## Was previously in config.py
from werkzeug.utils import send_from_directory


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or '/tmp'
    LOG_VERBOSITY = os.environ.get('LOG_VERBOSITY') or 'DEBUG'
    # HOST_ADDR = os.environ.get('HOST_ADDR') or '0.0.0.0'  # 127.0.0.1 for DEV, 0.0.0.0 for PROD
    # HOST_ADDR = os.environ.get('MASTER_IP') or '0.0.0.0'
    BASIC_AUTH_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'p@$$w0rd'
    CURRENT_FILE = 'TBD'
    DEBUG_TB_INTERCEPT_REDIRECTS = False


# Initialize the app... populate app.config[]
app = Flask(__name__)
app.config.from_object(Config)
app.static_folder = 'static'

# Set log verbosity based on environment
if app.config['LOG_VERBOSITY'] == 'DEBUG':
  app.debug = True    # for debugging...set False to turn off the DebugToolbarExtension
else:
  app.debug = False   # for debugging...set False to turn off the DebugToolbarExtension

# From The Flask Mega-Tutorial Part VII: Error Handling
if not os.path.exists('logs'):
  os.mkdir('logs')
file_handler = RotatingFileHandler('logs/ohscribe.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
  '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))

app.logger.addHandler(file_handler)
file_handler.setLevel(logging.INFO)
app.logger.setLevel(logging.INFO)

if app.config['LOG_VERBOSITY'] == 'DEBUG':
  file_handler.setLevel(logging.DEBUG)
  app.logger.setLevel(logging.DEBUG)

app.logger.info('OHScribe startup with LOG_VERBOSITY = %s.', app.config['LOG_VERBOSITY'])

if __name__ == '__main__':      # development?  Returns false in production, I think.
    app.run()

# bootstrap = Bootstrap(app)
# host = app.config['HOST_ADDR']
# app.logger.info('OHScribe "host" = %s.', host)

## Per https://github.com/flask-extensions/Flask-SimpleLogin
# SimpleLogin(app)    ...perhaps it is too simple?

## Per http://flask-basicauth.readthedocs.io/en/latest/
# basic_auth = BasicAuth(app)     ...broken and no longer maintained
# app.config['BASIC_AUTH_USERNAME'] = 'admin'

## Per https://pypi.org/project/flask-htpasswd/
# app.config['FLASK_HTPASSWD_PATH'] = '/Users/mcfatem/.htpasswd'
# app.config['FLASK_SECRET'] = 'Hey Hey Kids, secure me!'
# htpasswd.init_app(app)

# from webapp import simple_routes, errors, actions
# from webapp import routes, errors, actions







## --------- routes.py ------------

# from ohscribe import app
# from flask import render_template, flash, redirect, url_for, request, send_file
# from forms import MainForm
# from actions import do_cleanup, do_transform, do_hms_conversion, do_speaker_tags, do_analyze, do_all, allowed_file
# from werkzeug.utils import secure_filename
# import sys
# import os

# ## From https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
# @app.route('/')
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
  global current_file
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
      # filename = secure_filename(file.filename)
      filename = file.filename

      folder = app.config['UPLOAD_FOLDER']
      app.logger.debug("folder at line 124 is: '%s'", folder)
      newpath = os.path.join(folder, filename)
      app.logger.debug("newpath at line 126 is: '%s'", newpath)

      try:
        file.save(newpath)
        flash("Your file has been successfully uploaded to {}".format(newpath), 'info')
        app.config['CURRENT_FILE'] = newpath
        current_file = newpath
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


# Route for displaying the uploaded file
@app.route('/uploads/<filename>')
def CURRENT_FILE(filename):
    return send_from_directory(os.environ.get('OHSCRIBE_UPLOAD_FOLDER'), filename)

# Route for handling download section
@app.route('/download')
def download_file( ):
  global current_file
  # target = app.config['CURRENT_FILE']
  target = current_file

  app.logger.info("Target output for download is: %s", target)
  dir, filename = os.path.split(target)
  return send_file(target, mimetype='text/xml', cache_timeout=0, attachment_filename=filename, as_attachment=True)

# Route for handling the main/control page
@app.route('/main', methods=['POST', 'GET'])
@app.route('/', methods=['POST', 'GET'])
def main( ):
  form = MainForm(request.form)
  if request.method == 'POST':
    return redirect(url_for('results'))
  return render_template('main.html', title='Controls', form=form)

# Route for handling the results page
@app.route('/results', methods=['POST', 'GET'])
def results( ):
  global current_file
  result = request.form
  method = request.method

  try:
    result['exit']
  except:
    pass
  else:
    exit(0)

  # filename = app.config['CURRENT_FILE']
  filename = current_file

  try:
    result['all']
  except:
    pass
  else:
    file, msg, details, guidance = do_all(filename)
    # app.config['CURRENT_FILE'] = file
    current_file = file
    return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  try:
    if result['actions'] and result['go']:
      action = str(result['actions'])
      app.logger.info("/results action is: %s", action)
      if action == "cleanup":
        file, msg, details, guidance = do_cleanup(filename)
        # app.config['CURRENT_FILE'] = file
        current_file = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "transform":
        file, msg, details, guidance = do_transform(filename)
        # app.config['CURRENT_FILE'] = file
        current_file = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "convert":
        file, msg, details, guidance = do_hms_conversion(filename)
        # app.config['CURRENT_FILE'] = file
        current_file = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "speakers":
        file, msg, details, guidance = do_speaker_tags(filename)
        # app.config['CURRENT_FILE'] = file
        current_file = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)
      elif action == "analyze":
        file, msg, details, guidance = do_analyze(filename)
        # app.config['CURRENT_FILE'] = file
        current_file = file
        return render_template("results.html", result=result, message=msg, details=details, guidance=guidance)

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))







## --------- actions.py ------------

import os
import io
import sys
import re
from lxml import etree

# Internal / support functions go here.
# -------------------------------------------------------------------------

def allowed_file(filename):
  ALLOWED_EXTENSIONS = set(['xml'])
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def checkfile(filename):
  app.logger.debug('checkfile(%s) called.', filename)

  folder = app.config['UPLOAD_FOLDER']
  if '/' in filename:
    filepath = filename
  else:
    filepath = "{0}/{1}".format(folder, filename)
  msg = "checkfile( ) returning"
  app.logger.debug('checkfile(%s) returning %s.', filename, filepath)

  return filepath


def sanitize_xml(line):

  lead_double = u"\u201c"
  follow_double = u"\u201d"
  lead_single = u"\u2018"
  follow_single = u"\u2019"
  ellipsis = '&#8230;'
  endash = '&#8211;'
  emdash = '&#8212;'
  single = '&#8217;'

  line = line.replace('&lt;', '<').replace('&gt;', '>').replace(' & ', ' &amp; ').replace('<speaker>', '\n    <speaker>')
  line = line.replace(lead_double, '"').replace(follow_double, '"').replace(lead_single, "'").replace(follow_single, "'").replace(ellipsis, "...").replace(endash, '-').replace(emdash, '--').replace(single, "'")
  line = line.strip('\n')
  line = ' '.join(line.split())    # change any 'whitespace' characters to legitimate spaces.  Removes things like vertical tabs, 0xb.

  if len(line) > 0:                # don't return any empty lines!
    return "{}\n".format(line)
  else:
    return False


# Transform any XML with a XSLT
# Lifted from https://gist.github.com/revolunet/1154906

def xsl_transformation(xmlfile):
  if __name__ == '__main__':  # development?  Returns false in production, I think.
    xslfile = "ohscribe.xsl"
  else:
    xslfile = "/var/www/webroot/ROOT/ohscribe.xsl"
  
  # lifted from https://www.geeksforgeeks.org/file-searching-using-python/
  dir_path = os.path.dirname(os.path.realpath(__file__))
  for root, dirs, files in os.walk(dir_path):
    for file in files:
      if file.endswith('ohscribe.xsl'):
        xslfile = root + '/' + str(file)
        print(xslfile)

  try:
    with open(xslfile, 'r') as xsl:
      xslt = xsl.read( )
      root = etree.XML(xslt)
      transform = etree.XSLT(root)
      xml = xmlfile.read( )
      f = io.StringIO(xml)
      doc = etree.parse(f)
      result = transform(doc)

  except ValueError as err:
    msg = "XML Value error: {}".format(repr(err))
    flash(msg, 'error')
    raise

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise

  return result


# Return a new file name with '-insert' added before the .ext
# IOH now treats an underscore here as indication of a language, like _english, so change any/all underscores to dashes!

def make_new_filename(input_file_name, insert):
  input_file_name.replace("_", "-")
  name, ext = os.path.splitext(input_file_name)
  ret = "{name}-{insert}{ext}".format(name=name, insert=insert, ext=ext)
  return ret


# Actions here.
# ------------------------------------------------------------


# Cleanup the XML

def do_cleanup(filename):
  app.logger.debug('do_cleanup(%s) called.', filename)
  filepath = checkfile(filename)
  clean = make_new_filename(filepath, 'clean')
  app.logger.debug('do_cleanup(%s) returns %s as clean filename.', filename, clean)

  try:
    with open(filepath, 'r') as xmlfile, open(clean, 'w+') as cleanfile:
      app.logger.debug('do_cleanup(%s) opened %s as xmlfile and %s as cleanfile.', filename, filepath, clean)
      if xmlfile.name.rsplit(".")[-1] != "xml":
        msg = "File name should have a .xml extension!"
        flash(msg, 'warning')

      counter = 0
      for line in xmlfile:
        cleaned = sanitize_xml(line)
        if cleaned:
          cleanfile.write(cleaned)
          counter += 1

    # Parse the cleaned XML per https://lxml.de/parsing.html just to see if it is valid.
    parser = etree.XMLParser(ns_clean=True)

    try:
      tree = etree.parse(clean, parser)
    except:
      num_errors = len(parser.error_log)
      msg = "{0} parsed with an error_log count of {1}".format(clean, num_errors)
      flash(msg, 'error')
      error = parser.error_log[0]
      msg = "Parser error: '{0}' at line {1}, column {2}".format(error.message, error.line, error.column)
      flash(msg, 'error')
      raise

    with open(clean, 'r') as cleanfile:
      msg = "Clean-up is complete. {0} lines of '{1}' were processed to create '{2}'.".format(counter, filename, clean)
      flash(msg, 'info')
      detail = " ".join(cleanfile.readlines( )[0:10])
      guidance = "Please download your 'clean' output, upload that file, and engage the 'Transform' feature to change '{}' into proper IOH XML format.".format(clean)

    return clean, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise


# Transform XML from InqScribe to IOH

def do_transform(filename):
  app.logger.debug('do_transform(%s) called.', filename)
  filepath = checkfile(filename)

  try:
    with open(filepath, 'r+') as xmlfile:

      # Now transform it
      IOH_xml = xsl_transformation(xmlfile)
      if IOH_xml is None:
        msg = "Error transforming file `{}'.".format(filepath)
        flash(msg, 'error')
        return filepath, msg, "", ""

      ioh = make_new_filename(filepath, 'IOH')

      ioh_file = open(ioh, "w")
      ioh_file.write(str(IOH_xml))
      ioh_file.close()
      msg = "XML transformation output is in {}".format(ioh)
      flash(msg, 'info')

    with open(ioh, 'r') as xfile:
      # Number all the <cue> tags
      q = etree.parse(xfile)
      cue_tags = q.findall('.//cue')
      num = 0

      for tag in cue_tags:
        tag.set('cuenum', str(num))
        num += 1

      string = etree.tostring(q, pretty_print=True)

      iohx = make_new_filename(filepath, 'IOHx')

      ioh_file = open(iohx, "wb")
      ioh_file.write(string)
      ioh_file.close()
      msg = "XML transformation output with numbered cues is in {}".format(iohx)
      flash(msg, 'info')

    with open(iohx, 'r') as transfile:
      msg = "XSLT transformation is complete and the cue-numbered results are in '{}'.".format(iohx)
      detail = " ".join(transfile.readlines( )[0:10])
      guidance = "Please download your 'transformed' output, upload that file, and engage the 'Convert hh:mm:ss...' feature to change time references in '{}'".format(ioh_file)

    return iohx, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise


# Convert hh:mm:ss times to seconds

def do_hms_conversion(filename):
  app.logger.debug('do_hms_conversion(%s) called.', filename)
  filepath = checkfile(filename)
  secname = make_new_filename(filepath, 'sec')

  try:
    with open(filepath, 'r') as xmlfile, open(secname, 'w') as secfile:
      counter = 0

      for line in xmlfile:
        matched = re.match(r'(.*)(\d\d:\d\d:\d\d\.\d\d)(.*)', line)
        if matched:
          hms = matched.group(2)
          h, m, s = hms.split(':')
          sec = str(int(h) * 3600 + int(m) * 60 + float(s))
          line = line.replace(hms, sec)
          counter += 1
        secfile.write(line)

      msg = "hh:mm:ss conversion output is in {0} with {1} modified lines".format(secname, counter)
      flash(msg, 'info')

    with open(secname, 'r') as secfile:
      msg = "Conversion of hh:mm:ss times to seconds is complete.  Results are in '{}'.".format(secname)
      detail = " ".join(secfile.readlines()[0:10])
      guidance = "Please download your 'time-converted' output, upload that file, and engage the 'Format Speaker Tags' feature to change speaker tags in '{}'".format(secfile)

    return secname, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise


# Format <speaker> tags

def do_speaker_tags(filename):
  app.logger.debug('do_speaker_tags(%s) called.', filename)
  filepath = checkfile(filename)
  final = make_new_filename(filepath, 'final')

  try:
    with open(filepath, 'r') as xmlfile, open(final, 'wb') as finalfile:

      # Identify all <speaker> tags
      q = etree.parse(xmlfile)

      speaker_tags = q.findall('.//speaker')
      speakers = dict()
      num = 1

      for tag in speaker_tags:
        if tag.text:
          full = tag.text.strip( )
          try:
            first, rest = full.split(' ', 1)
          except ValueError:
            first = full

          first = first.replace('_', ' ').strip( )      # replace any underscores with spaces and trim
          full = full.replace('_', ' ')

          if first not in speakers:
            speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>", 'full_name': full}
            num += 1

      # Examine each <cue>. Identify speakers in the transcript.text and modify that text accordingly
      cue_tags = q.findall('.//cue')

      for tag in cue_tags:
        cuenum = tag.attrib['cuenum']
        t = tag.find('transcript')
        text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')

        words = text.split()
        t.text = ''
        count = 0
        speakers_found = []

        app.logger.debug('do_speaker_tags( ) processing text: %s', text)

        for word in words:
          app.logger.debug('do_speaker_tags( ) word is: %s', word)

          # Found a speaker reference (ends in '...| ')
          if word.endswith('|'):
            s = word.replace('_', ' ')      # replace any underscores with spaces in the speaker name
            speaker = s.strip('|')

            if speaker in speakers:
              if count > 0:
                t.text += '</span></span>'
              t.text += speakers[speaker]['class'] + speaker + ": " + "<span class='oh_speaker_text'>"

              if speaker not in speakers_found:
                speakers_found.append(speaker)
              count += 1

            else:
              msg = "Referenced speaker '{}' has no corresponding <speaker> tag!".format(speaker)
              flash(msg, 'error')

          else:
            t.text += " " + word

        t.text += '</span></span>'

        # Was there ANY speaker | reference?  If not...
        if not speakers_found:
          msg = "There is NO speaker identifed in <cue> {0}!  Reminder: There must be a space following the bar seperator.".format(cuenum)
          flash(msg, 'error')
        else:        # Now build a proper <speaker> tag from the references found, and apply it
          speaker_tag = ''
          for speaker in speakers_found:
            speaker_tag += speakers[speaker]['full_name'] + ' & '
          speaker_tag = speaker_tag.strip(' & ')

          t = tag.find('speaker')
          t.text = speaker_tag

      finalfile.write(etree.tostring(q, pretty_print=True))

    with open(final, 'r') as finalfile:
      msg = "Speaker formatting in transcript '{}' is complete.".format(final)
      flash(msg, 'info')
      detail = " ".join(finalfile.readlines()[0:20])
      guidance = "Please download your 'speaker-tagged' output, upload that file, and engage the 'Analyze' feature on '{}' to flag <cues> that are potentially too long.".format(final)

    return final, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise


# Analyze and report <cue> lengths

def do_analyze(filename):
  app.logger.debug('do_analyze(%s) called.', filename)
  filepath = checkfile(filename)

  try:
    with open(filepath, 'r+') as xmlfile:

      problem_cues = "Long cue start times: "
      problems = 0
      q = etree.parse(xmlfile)
      cue_tags = q.findall('.//cue')
      cue_num = 0

      for tag in cue_tags:
        t = tag.find('start')
        start = int(float(t.text))
        m, s = divmod(start, 60)
        cue_start = '{:d}:{:02d} '.format(m, s)

        t = tag.find('transcript')
        text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')

        words = text.split()
        cue_lines = 0
        cue_chars = 0
        assumed_line_max = 80    # assuming 80 characters per line for a max target

        for word in words:
          if word.endswith('>'):  # ignore all tags
            continue
          if word.startswith('<'):  # ignore all tags
            continue

          if word.endswith(':'):  # found a new speaker, new line
            cue_lines += 1
            cue_chars = len(word) - 20  # accounts for the class='oh_speaker_x'> tag

          else:
            cue_chars += len(word) + 1
            if cue_chars > assumed_line_max:
              cue_lines += 1
              cue_chars = 0

        # Done with cue text analysis... report if necessary
        app.logger.debug('do_analyze( ) done with cue %s text analysis with %s lines.', cue_num, cue_lines)

        if cue_lines == 0:
          msg = "Cue `{}' is EMPTY. Remove that cue before proceeding!".format(cue_num)
          flash(msg, 'error')

        if cue_lines > 10:
          problem_cues += str(cue_start)
          problems += 1

        cue_num += 1
        app.logger.debug('do_analyze( ) advancing to cue_num %s.', cue_num)

      # Analysis is complete.  Report
      app.logger.debug('do_analyze( ) analysis is complete. Number of problems is: %s', problems)

      if problems > 0:
        msg = "One or more long cues were found in '{}'".format(filename)
        flash(msg, 'warning')
        guidance = "Please visit the transcript XML and consider dividing these cues into smaller sections."
        return filepath, msg, problem_cues, guidance

      if problems == 0:
        msg = "Analysis is complete and there were NO additional problems found in transcript `{}'.".format(filename)
        flash(msg, 'info')

    return filepath, msg, "", ""

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    raise


# Do all of the above, in sequence.

def do_all(filename):
  global current_file
  app.logger.debug('do_all(%s) called.', filename)
  filepath = checkfile(filename)
  clean, msg, details, guidance = do_cleanup(filepath)
  # app.config['CURRENT_FILE'] = clean
  current_file = clean
  xformed, msg, details, guidance = do_transform(clean)
  # app.config['CURRENT_FILE'] = xformed
  current_file = xformed
  times, msg, details, guidance = do_hms_conversion(xformed)
  # app.config['CURRENT_FILE'] = times
  current_file = times
  final, msg, details, guidance = do_speaker_tags(times)
  # app.config['CURRENT_FILE'] = final
  current_file = final
  analyzed, msg, details, guidance = do_analyze(final)
  app.logger.info("Final output is in: %s", final)
  return analyzed, msg, details, guidance


  #
  # def button_reformat_callback():
  #   """ what to do when the "Reformat" button is pressed """
  #
  #   xmlfile = entry.get()
  #   if xmlfile.rsplit(".")[-1] != "xml":
  #     statusText.set("Filename must have a .xml extension!")
  #     message.configure(fg="red")
  #     return
  #
  #   IOH_xmlfile = get_IOH_filename(xmlfile)
  #   copyfile(xmlfile, IOH_xmlfile)
  #
  #   """ make it pretty """
  #   parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
  #   document = etree.parse(IOH_xmlfile, parser)
  #   document.write(IOH_xmlfile, pretty_print=True, encoding='utf-8')
  #
  #   """ identify all the speaker tags """
  #   q = etree.parse(IOH_xmlfile)
  #   speaker_tags = q.findall('.//speaker')
  #   speakers = dict()
  #   num = 1
  #
  #   for tag in speaker_tags:
  #     if tag.text:
  #       full = tag.text.strip()
  #       if ' ' not in full:
  #         first = full
  #       else:
  #         first, rest = full.split(' ', 1)
  #
  #       first = first.strip()
  #       if first not in speakers:
  #         speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>", 'full_name': full}
  #         num += 1
  #
  #   """ examine each cue, identify THE speaker and modify the cue accordingly """
  #   cue_tags = q.findall('.//cue')
  #   speakers_found = []
  #
  #   for tag in cue_tags:
  #     s = tag.find('speaker')
  #     if ' ' not in s.text.strip():
  #       first = s.text.strip()
  #     else:
  #       first, rest = s.text.strip().split(' ', 1)
  #     first = first.strip()
  #     if first not in speakers_found:
  #       speakers_found.append(first)
  #     t = tag.find('transcript')
  #     if t.text is None:
  #       statusText.set("Transcript has no text at source line " + str(t.sourceline) + "!")
  #       message.configure(fg="red")
  #       return
  #
  #     text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
  #     t.text = ''
  #     try:
  #       t.text += speakers[first]['class'] + first + ": " + "<span class='oh_speaker_text'>" + text + '</span></span>'
  #     except KeyError:
  #       statusText.set("Transcript 'KeyError' at source line " + str(t.sourceline) + "! Please investigate.")
  #       message.configure(fg="red")
  #       return
  #
  #   q.write(IOH_xmlfile)
  #   entry.delete(0, END)
  #   entry.insert(0, IOH_xmlfile)
  #
  #   statusText.set("Speaker reformatting for transcript `{}' is complete.".format(IOH_xmlfile))
  #   message.configure(fg="dark green")



# Pretty-print the XML   @TODO Broken.  No longer worth the effort?

# def do_pretty(filename):
#   flash("Now inside the do_pretty function.", 'info')
#
#   filepath = "{0}/{1}".format(app.config['UPLOAD_FOLDER'], filename)
#   flash("Attempting to open '{}'.".format(filepath), 'info')
#   result = "Process is incomplete!"
#
#   pretty = make_new_filename(filepath, 'pretty')
#
#   # Make it pretty
#
#   try:
#     with open(filepath, 'r') as xmlfile, open(pretty, 'w+') as prettyfile:
#       try:
#         bs = BeautifulSoup(xmlfile)
#         prettyfile.write(bs.prettify( ))
#         flash(bs.prettify( ), 'info')
#       except:
#         msg = "Unexpected error: {}".format(sys.exc_info()[0])
#         flash(msg, 'error')
#         return redirect(url_for('main'))
#
#     flash("XML pretty-print has been applied in '{}'.".format(pretty), 'info')
#
#     result = "Pretty-printing is complete. File '{0}' was processed to create '{1}'.".format(filename, pretty)
#
#   except:
#     msg = "Unexpected error: {}".format(sys.exc_info()[0])
#     flash(msg, 'error')
#     return redirect(url_for('main'))
#
#   return result








## --------- errors.py ------------

@app.errorhandler(401)
def unauthorized(error):
    return render_template('401.html'), 401

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return render_template('405.html'), 405

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500





## --------- forms.py ------------

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

#
# class LoginForm(FlaskForm):
#   username = StringField('Username', validators=[DataRequired()])
#   password = PasswordField('Password', validators=[DataRequired()])
#   # remember_me = BooleanField('Remember Me')
#   submit = SubmitField('Sign In')
#
#
#

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
