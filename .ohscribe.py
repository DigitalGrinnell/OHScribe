from webapp import app

# import os.path
# import fileinput
# import StringIO
# from lxml import etree
# from shutil import copyfile
#
# """
# This code lifted from my previous Transform_InqScribe_to_IOH project and .py file by the same name, with all Tk parts removed.  8^)
#
#
#
# https://acaird.github.io/2016/02/07/simple-python-gui
#
# Transform_InqScribe_to_IOH.py
#
# Python2 script to parse transcription XML output from InqScribe and translate
# to the native <cues> structure required for the Islandora Oral Histories Solution Pack
# (https://github.com/digitalutsc/islandora_solution_pack_oralhistories).
#
# Basic GUI with command-line option lifted from https://acaird.github.io/2016/02/07/simple-python-gui
# source.
#
# """
#
#
#
# def get_IOH_filename(input_file_name):
#   """ IOH now treats an underscore here as indication of a language, like _english, so change any/all underscores to dashes! """
#   input_file_name.replace("_", "-")
#   parts = os.path.split(input_file_name)
#   return parts[0] + "/IOH-" + parts[1]
#
#
# def button_transform_callback(filename):
#   """ what to do when the "Transform" button is pressed """
#   xmlfile = open(filename, 'r')
#
#   if xmlfile.rsplit(".")[-1] != "xml":
#     msg = "Filename must have a .xml extension!"
#     flash(msg, 'error')
#     return
#   else:
#
#     """ clean up the XML first """
#     x = fileinput.input(xmlfile, inplace=1)
#     for line in x:
#       line = line.replace('&lt;', '<')
#       line = line.replace('&gt;', '>')
#       print line,
#     x.close()
# 
#     """ read the file again looking for looooooonnnnnnng scenes """
#     x = fileinput.input(xmlfile, inplace=1)
#     lineCount = 0;
#     numChar = 0;
#
#     """ make it pretty """
#     parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
#     document = etree.parse(xmlfile, parser)
#     document.write(xmlfile, pretty_print=True, encoding='utf-8')
#
#     """ now transform it """
#     IOH_xml = xsl_transformation(xmlfile)
#     if IOH_xml is None:
#       msg = "Error transforming file `{}'.".format(xmlfile)
#       flash(msg, 'error')
#       return
#
#     output_file_name = get_IOH_filename(xmlfile)
#
#     ioh_file = open(output_file_name, "w")
#     if ioh_file:
#       ioh_file.write(str(IOH_xml))
#       ioh_file.close()
#       msg = "Output is in {}".format(output_file_name)
#       flash(msg, 'info')
#       # entry.delete(0, END)
#       # entry.insert(0, output_file_name)
#
#     else:
#       msg = "File `{}' could not be opened for output.".format(output_file_name)
#       flash(msg, 'error')
#

# def button_hms_callback():
#   """ what to do when the "Convert hh:mm:ss..." button is pressed """
#
#   xmlfile = entry.get()
#
#   if xmlfile.rsplit(".")[-1] != "xml":
#     statusText.set("Filename must have a .xml extension!")
#     message.configure(fg="red")
#     return
#   else:
#
#     x = fileinput.input(xmlfile, inplace=1)
#     for line in x:
#       matched = re.match(r'(.*)(\d\d:\d\d:\d\d\.\d\d)(.*)', line)
#       if matched:
#         hms = matched.group(2)
#         h, m, s = hms.split(':')
#         sec =  str(int(h) * 3600 + int(m) * 60 + float(s))
#         line = line.replace(hms, sec)
#       print line,
#
#     x.close()
#     statusText.set("hh:mm:ss values in `{}' have been converted to seconds.".format(xmlfile))
#     message.configure(fg="dark green")
#
#
# def button_format_callback():
#   """ what to do when the "Format" button is pressed """
#
#   xmlfile = entry.get()
#
#   if xmlfile.rsplit(".")[-1] != "xml":
#     statusText.set("Filename must have a .xml extension!")
#     message.configure(fg="red")
#     return
#
#   else:
#     """ identify all the speaker tags """
#     q = etree.parse(xmlfile)
#     speaker_tags = q.findall('.//speaker')
#     speakers = dict()
#     num = 1
#
#     for tag in speaker_tags:
#       if tag.text:
#         full = tag.text.strip()
#         first, rest = full.split(' ', 1)
#         first = first.strip()
#         if first not in speakers:
#           speakers[first] = {'number':num, 'class':"<span class='oh_speaker_" + str(num) + "'>", 'full_name':full}
#           num += 1
#
#     """ examine each cue, identify speakers in the transcript.text and modify that text accordingly """
#     cue_tags = q.findall('.//cue')
#     for tag in cue_tags:
#       t = tag.find('transcript')
#       text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
#
#       words = text.split()
#       t.text = ''
#       count = 0
#       speakers_found = []
#
#       for word in words:
#         if word.endswith('|'):
#           speaker = word.strip('|')
#
#           if speaker in speakers:
#             if count > 0:
#               t.text += '</span></span>'
#             t.text += speakers[speaker]['class'] + speaker + ": " + "<span class='oh_speaker_text'>"
#             # t.text += "<span class='oh_speaker'>" + speaker + ': ' + speakers[speaker]['class']
#
#             if speaker not in speakers_found:
#               speakers_found.append(speaker)
#             count += 1
#           else:
#             statusText.set("Referenced speaker '" + speaker + "' has no corresponding <speaker> tag!")
#             message.configure(fg="red")
#             return
#         else:
#           t.text += ' ' + word
#
#       t.text += '</span></span>'
#
#       """ now build a proper <speaker> tag from the references found, and apply it """
#       speaker_tag = ''
#       for speaker in speakers_found:
#         speaker_tag += speakers[speaker]['full_name'] + ' & '
#       speaker_tag = speaker_tag.strip(' & ')
#
#       t = tag.find('speaker')
#       t.text = speaker_tag
#
#     q.write(xmlfile)
#
#     statusText.set("Speaker formatting for transcript `{}' is complete.".format(xmlfile))
#     message.configure(fg="dark green")
#
#
# def button_analyze_callback():
#   """ what to do when the "Analyze" button is pressed """
#
#   xmlfile = entry.get()
#
#   if xmlfile.rsplit(".")[-1] != "xml":
#     statusText.set("Filename must have a .xml extension!")
#     message.configure(fg="red")
#     return
#
#   else:
#     """ examine each cue, count number of lines of text and report any longer than 10 lines """
#     problem_cues = "Long cue start times: "
#     problems = 0
#     q = etree.parse(xmlfile)
#     cue_tags = q.findall('.//cue')
#     cue_num = 0
#
#     for tag in cue_tags:
#       t = tag.find('start')
#       start = int(float(t.text))
#       m, s = divmod(start, 60)
#       cue_start = '{:d}:{:02d} '.format(m,s)
#
#       t = tag.find('transcript')
#       text = t.text.replace('\n', ' ').replace('  ', ' ').replace(' :', ':').replace(' |', '|')
#
#       words = text.split()
#       cue_lines = 0
#       cue_chars = 0
#       assumed_line_max = 80  # assuming 80 characters per line for a max target
#
#       for word in words:
#         if word.endswith('>'):    # ignore all tags
#           continue
#         if word.startswith('<'):  # ignore all tags
#           continue
#
#         if word.endswith(':'):    # found a new speaker, new line
#           cue_lines += 1
#           cue_chars = len(word) - 20    # accounts for the class='oh_speaker_x'> tag
#
#         else:
#           cue_chars += len(word) + 1
#           if cue_chars > assumed_line_max:
#             cue_lines += 1
#             cue_chars = 0
#
#       """ done with cue text analysis...report if necessary """
#       if cue_lines == 0:
#         statusText.set("Cue `{}' is EMPTY. Remove it before proceeding!".format(cue_num))
#         message.configure(fg="red")
#         return
#       if cue_lines > 10:
#         problem_cues += str(cue_start)
#         problems += 1
#       cue_num += 1
#
#     """ analysis is complete.  report """
#     if problems == 0:
#       statusText.set("Analysis is complete, no problems found in transcript `{}'.".format(xmlfile))
#       message.configure(fg="dark green")
#       return
#
#     if problems > 0:
#       statusText.set(problem_cues)
#       message.configure(fg="red")
#       return
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
#
#
# def button_browse_callback():
#   """ What to do when the Browse button is pressed """
#   filename = tkFileDialog.askopenfilename()
#   entry.delete(0, END)
#   entry.insert(0, filename)
#
# # Transform any XML with a XSLT
# # Lifted from https://gist.github.com/revolunet/1154906
#
# def xsl_transformation(xmlfile, xslfile="./Transform_InqScribe_to_IOH.xsl"):
#
#   xsl = open(xslfile)
#   if xsl:
#     xslt = xsl.read()
#   else:
#     statusText.set("XSLT file `{}' could not be opened.".format(xslfile))
#     message.configure(fg="red")
#
#   xslt_tree = etree.XML(xslt)
#   transform = etree.XSLT(xslt_tree)
#
#   xml = open(xmlfile)
#   if xml:
#     xml_contents = xml.read()
#   else:
#     statusText.set("XML file `{}' could not be opened.".format(xmlfile))
#     message.configure(fg="red")
#
#   f = StringIO.StringIO(xml_contents)
#   doc = etree.parse(f)
#   f.close()
#   transform = etree.XSLT(xslt_tree)
#   result = transform(doc)
#
#   return result
