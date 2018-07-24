from app import app
from flask import flash, redirect, url_for
# from werkzeug.utils import secure_filename
import os
import io
import sys
import re
import logging
from lxml import etree

# Internal / support functions go here.
# -------------------------------------------------------------------------


def allowed_file(filename):
  ALLOWED_EXTENSIONS = set(['xml'])
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# def upload_to_server(request, filename):
#   flash("upload_to_server called with file '{}'".format(filename), 'info')
#   if (allowed_file(filename)):
#     filepath = checkfile(filename)
#     with open(filepath, 'r') as xmlfile:
#       flash("The file at path '{}' is open for upload".format(filepath), 'info')
#       upfilename = secure_filename(xmlfile.filename)
#       xmlfile.save(os.path.join(environ.get('OHSCRIBE_UPLOAD_FOLDER'), upfilename))
#       flash("File has been uploaded and named '{}'".format(upfilename), 'info')
#       return True
#   else:
#     flash("Only .xml files are allowed for upload.  Please Exit or choose a suitable file and try again.", 'error')
#     return False
#
#   #
#   #   # if request.method == 'POST':
#   #   # Check if the post request has the file part
#   #   # if 'file' not in request.files:
#   #   #   flash('No file part')
#   #   #   return redirect(request.url)
#   #   file = request.files['file']
#   #   if file and allowed_file(file.filename):
#   #     filename = secure_filename(file.filename)
#   #     file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#   #     return True  # redirect(url_for('CURRENT_FILE', filename=filename))
#   # return '''
#   # <!doctype html>
#   # <title>Upload new File</title>
#   # <h1>Upload new File</h1>
#   # <form method=post enctype=multipart/form-data>
#   # <input type=file name=file>
#   # <input type=submit value=Upload>
#   # </form>
#   # '''


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
  
  line = line.replace('&lt;', '<').replace('&gt;', '>').replace(' & ', ' &amp; ').replace('<speaker>', '\n    <speaker>')
  line = line.replace(lead_double, '"').replace(follow_double, '"').replace(lead_single, "'").replace(follow_single, "'")
  line = line.strip('\n')
  line = ' '.join(line.split())    # change any 'whitespace' characters to legitimate spaces.  Removes things like vertical tabs, 0xb.
  
  if len(line) > 0:                # don't return any empty lines!
    return "{}\n".format(line)
  else:
    return False


# Transform any XML with a XSLT
# Lifted from https://gist.github.com/revolunet/1154906

def xsl_transformation(xmlfile, xslfile="/app/ohscribe.xsl"):
  app.logger.debug('xsl_transformation(xmlfile, %s) called.', xslfile)

  try:
    app.logger.debug('xsl_transformation calling open(xslfile).')
    with open(xslfile, 'r') as xsl:
      app.logger.debug('xsl_transformation calling xsl.read( ).')
      xslt = xsl.read( )
      app.logger.debug('xsl_transformation calling etree.XML(xslt).')
      root = etree.XML(xslt)
      app.logger.debug('xsl_transformation calling etree.XSLT(root).')
      transform = etree.XSLT(root)
      app.logger.debug('xsl_transformation calling xmlfile.read().')
      xml = xmlfile.read( )
      app.logger.debug('xsl_transformation calling io.StringIO(xml).')
      f = io.StringIO(xml)
      app.logger.debug('xsl_transformation calling etree.parse(f).')
      doc = etree.parse(f)
      app.logger.debug('xsl_transformation calling transform(doc).')
      result = transform(doc)

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
    raise

  app.logger.debug('xsl_transformation(xmlfile, %s) returning %s.', xslfile, result)
  return result


# Return a new file name with '-insert' added before the .ext
# IOH now treats an underscore here as indication of a language, like _english, so change any/all underscores to dashes!

def make_new_filename(input_file_name, insert):
  app.logger.debug('make_new_filename(%s, %s) called.', input_file_name, insert)
  input_file_name.replace("_", "-")
  name, ext = os.path.splitext(input_file_name)
  ret = "{name}-{insert}{ext}".format(name=name, insert=insert, ext=ext)
  app.logger.debug('make_new_filename(%s, %s) returning %s.', input_file_name, insert, ret)
  return ret


# Actions here.
# ------------------------------------------------------------


# Cleanup the XML

def do_cleanup(filename):
  app.logger.debug('do_cleanup(%s) called.', filename)
  filepath = checkfile(filename)
  clean = make_new_filename(filepath, 'clean')

  try:
    app.logger.debug('do_cleanup( ) calling open(%s) and open(%s).', filepath, clean)
    with open(filepath, 'r') as xmlfile, open(clean, 'w+') as cleanfile:
      if xmlfile.name.rsplit(".")[-1] != "xml":
        app.logger.debug('do_cleanup( ) extension is not .xml!')
        msg = "File name should have a .xml extension!"
        flash(msg, 'warning')

      counter = 0
      app.logger.debug('do_cleanup( ) line counter is: %s.', counter)
      for line in xmlfile:
        cleaned = sanitize_xml(line)
        app.logger.debug('do_cleanup( ) counter and cleaned are: %s, %s.', counter, cleaned)
        if cleaned:
          app.logger.debug('do_cleanup( ) writing line to cleanfile.')
          cleanfile.write(cleaned)
          counter += 1

    # Parse the cleaned XML per https://lxml.de/parsing.html just to see if it is valid.
    app.logger.debug('do_cleanup( ) calling etree.XMLParser( ).')
    parser = etree.XMLParser(ns_clean=True)
    app.logger.debug('do_cleanup( ) returned from etree.XMLParser( ).')

    try:
      app.logger.debug('do_cleanup( ) calling etree.parse( ).')
      tree = etree.parse(clean, parser)
      app.logger.debug('do_cleanup( ) returned from etree.parse( ).')
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
      guidance = "Please return to Main/Control and engage the 'Transform' feature to change '{}' into proper IOH XML format.".format(clean)

    return clean, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
    raise


# Transform XML from InqScribe to IOH

def do_transform(filename):
  app.logger.debug('do_transform(%s) called.', filename)
  filepath = checkfile(filename)

  try:
    app.logger.debug('do_transform(%s) calling open(%s).', filename, filepath)
    with open(filepath, 'r+') as xmlfile:

      # Now transform it
      app.logger.debug('do_transform( ) calling xsl_transformation( ).')
      IOH_xml = xsl_transformation(xmlfile)
      if IOH_xml is None:
        app.logger.debug('do_transform( ) encountered a transform error.')
        msg = "Error transforming file `{}'.".format(filepath)
        flash(msg, 'error')
        return filepath, msg, "", ""

      ioh = make_new_filename(filepath, 'IOH')

      app.logger.debug('do_transform( ) calling open(%s).', ioh)
      ioh_file = open(ioh, "w")
      ioh_file.write(str(IOH_xml))
      ioh_file.close()
      msg = "XML transformation output is in {}".format(ioh)
      flash(msg, 'info')
      app.logger.debug('do_transform( ) transformation is in %s.', ioh)

    app.logger.debug('do_transform( ) calling open(%s) as xfile.', ioh)
    with open(ioh, 'r') as xfile:
      # Number all the <cue> tags
      app.logger.debug('do_transform( ) calling q=etree.parse( )')
      q = etree.parse(xfile)
      app.logger.debug('do_transform( ) calling q=findall(.//cue)')
      cue_tags = q.findall('.//cue')
      num = 0

      for tag in cue_tags:
        app.logger.debug('do_transform( ) calling tag.set for number %s.', num)
        tag.set('cuenum', str(num))
        num += 1

      app.logger.debug('do_transform( ) calling etree.tostring( )')
      string = etree.tostring(q, pretty_print=True)

      iohx = make_new_filename(filepath, 'IOHx')

      app.logger.debug('do_transform( ) calling open(%s) as iohx', iohx)
      ioh_file = open(iohx, "wb")
      ioh_file.write(string)
      ioh_file.close()
      msg = "XML transformation output with numbered cues is in {}".format(iohx)
      flash(msg, 'info')
      app.logger.debug('do_transform( ) transformed output with numbered cues in %s.', iohx)

    with open(iohx, 'r') as transfile:
      msg = "XSLT transformation is complete and the cue-numbered results are in '{}'.".format(iohx)
      detail = " ".join(transfile.readlines( )[0:10])
      guidance = "Please return to Main/Control and engage the 'Convert hh:mm:ss...' feature to change time references in '{}'".format(ioh_file)

    return iohx, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
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
      guidance = "Please return to Main/Control and engage the 'Format Speaker Tags' feature to change speaker tags in '{}'".format(secfile)

    return secname, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
    raise


# Format <speaker> tags

def do_speaker_tags(filename):
  app.logger.debug('do_speaker_tags(%s) called.', filename)
  filepath = checkfile(filename)
  final = make_new_filename(filepath, 'final')

  try:
    app.logger.debug('do_speaker_tags calling open(%s) and open(%s).', filepath, final)
    with open(filepath, 'r') as xmlfile, open(final, 'wb') as finalfile:

      # Identify all <speaker> tags

      app.logger.debug('do_speaker_tags calling etree.parse(xmlfile).')
      q = etree.parse(xmlfile)

      app.logger.debug('do_speaker_tags calling q.findall(.//speaker).')
      speaker_tags = q.findall('.//speaker')
      speakers = dict()
      num = 1

      app.logger.debug('do_speaker_tags starting for tag in speaker_tags... loop.')
      for tag in speaker_tags:
        app.logger.debug('do_speaker_tags calling if tag.text:')
        if tag.text:
          full = tag.text.strip()
          app.logger.debug('do_speaker_tags full is: %s', full)
          first, rest = full.split(' ', 1)
          app.logger.debug('do_speaker_tags first, rest are: %s, %s', first, rest)
          first = first.strip()
          app.logger.debug('do_speaker_tags first stripped is: %s', first)
          if first not in speakers:
            app.logger.debug('do_speaker_tags %s is NOT in speakers!', first)
            speakers[first] = {'number': num, 'class': "<span class='oh_speaker_" + str(num) + "'>", 'full_name': full}
            num += 1

      # Examine each <cue>. Identify speakers in the transcript.text and modify that text accordingly

      app.logger.debug('do_speaker_tags calling q.findall(.//cue).')
      cue_tags = q.findall('.//cue')

      app.logger.debug('do_speaker_tags starting for tag in cue_tags... loop.')
      for tag in cue_tags:
        cuenum = tag.attrib['cuenum']
        app.logger.debug('do_speaker_tags cuenum is: %s', cuenum)
        t = tag.find('transcript')
        text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
        app.logger.debug('do_speaker_tags replaced text is: %s', text)

        words = text.split()
        t.text = ''
        count = 0
        speakers_found = []

        app.logger.debug('do_speaker_tags starting for word in words... loop.')
        for word in words:
          app.logger.debug('do_speaker_tags for words... word is: %s', word)
          if word.endswith('|'):
            app.logger.debug('do_speaker_tags word.endswith(|) so it is a speaker name.')
            s = word.replace('_', ' ')
            speaker = s.strip('|')
            app.logger.debug('do_speaker_tags speaker is: %s', speaker)

            if speaker in speakers:
              app.logger.debug('do_speaker_tags if speaker in speakers is true.')
              if count > 0:
                t.text += '</span></span>'
              t.text += speakers[speaker]['class'] + speaker + ": " + "<span class='oh_speaker_text'>"

              if speaker not in speakers_found:
                app.logger.debug('do_speaker_tags speaker is NOT in speakers_found!')
                speakers_found.append(speaker)
              count += 1

            else:
              msg = "Referenced speaker '{}' has no corresponding <speaker> tag!".format(speaker)
              flash(msg, 'error')
              return redirect(url_for('main'))

          else:
            app.logger.debug('do_speaker_tags word is not a speaker name so appending to t.text.')
            t.text += " " + word

        t.text += '</span></span>'
        app.logger.debug('do_speaker_tags complete t.text is: %s', t.text)

        # Now build a proper <speaker> tag from the references found, and apply it

        app.logger.debug('do_speaker_tags starting is speaker not in speakers_found... loop.')
        if speaker not in speakers_found:
          msg = "Speaker '{0}' was found in a <cue> {1} with NO correspinding <speaker> tag!".format(speaker, cuenum)
          flash(msg, 'warning')
          # return redirect(url_for('main'))

        speaker_tag = ''
        for speaker in speakers_found:
          speaker_tag += speakers[speaker]['full_name'] + ' & '
        speaker_tag = speaker_tag.strip(' & ')

        t = tag.find('speaker')
        t.text = speaker_tag

      app.logger.debug('do_speaker_tags calling finalfile.write()')
      finalfile.write(etree.tostring(q, pretty_print=True))

    with open(final, 'r') as finalfile:
      msg = "Speaker formatting in transcript '{}' is complete.".format(final)
      flash(msg, 'info')
      detail = " ".join(finalfile.readlines()[0:20])
      guidance = "Please return to Main/Control and engage the 'Analyze' feature on '{}' to flag <cues> that are potentially too long.".format(final)

    return final, msg, detail, guidance

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
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

        if cue_lines == 0:
          msg = "Cue `{}' is EMPTY. Remove that cue before proceeding!".format(cue_num)
          flash(msg, 'error')
          return redirect(url_for('main'))

        if cue_lines > 10:
          problem_cues += str(cue_start)
          problems += 1
        cue_num += 1

      # Analysis is complete.  Report

      if problems > 0:
        msg = "One or more long cues were found in '{}'".format(filename)
        flash(msg, 'warning')
        guidance = "Please visit the transcript XML and consider dividing these cues into smaller sections."
        return filepath, msg, problem_cues, guidance

      if problems == 0:
        msg = "Analysis is complete and there were NO problems found in transcript `{}'.".format(filename)
        flash(msg, 'info')

    return filepath, msg, "", ""

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    # return redirect(url_for('main'))
    raise


# Do all of the above, in sequence.

def do_all(filename):
  app.logger.debug('do_all(%s) called.', filename)
  filepath = checkfile(filename)
  clean, msg, details, guidance = do_cleanup(filepath)
  app.config['CURRENT_FILE'] = clean
  xformed, msg, details, guidance = do_transform(clean)
  app.config['CURRENT_FILE'] = xformed
  times, msg, details, guidance = do_hms_conversion(xformed)
  app.config['CURRENT_FILE'] = times
  final, msg, details, guidance = do_speaker_tags(times)
  app.config['CURRENT_FILE'] = final
  analyzed, msg, details, guidance = do_analyze(final)
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
