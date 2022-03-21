from webapp import app
from flask import flash
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

def xsl_transformation(xmlfile, xslfile="/app/ohscribe.xsl"):

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

  try:
    with open(filepath, 'r') as xmlfile, open(clean, 'w+') as cleanfile:
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
