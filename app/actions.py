from flask import flash, redirect, url_for
from app import app
import os
import io
import sys
from lxml import etree
from bs4 import BeautifulSoup
import re

# Internal / support functions go here.
# -------------------------------------------------------------------------


def sanitize_xml(line0):
  # pi = re.compile('<\?.+\?>')
  # line0 = re.sub(pi, "", line)                   # remove any <?...?> processing instructions
  line1 = line0.replace('&lt;', '<')             # replace &lt; with opening bracket
  line2 = line1.replace('&gt;', '>')             # replace &gt; with closing bracket
  line3 = line2.replace(' & ', ' &amp; ')        # replace all lone &'s with &amp;
  line4 = line3.replace('`', "'")                # replace "smart" quotes with plain ones!
  line5 = line4.strip('\n')                      # strip \n from start or end
  line6 = line5.replace('?>', '?>\n')            # ensure that processsing instructions are on their own line
  if len(line6) > 0:                             # don't return any empty lines!
    return "{}\n".format(line6)
  else:
    return False


# Transform any XML with a XSLT
# Lifted from https://gist.github.com/revolunet/1154906

def xsl_transformation(xmlfile, xslfile="./ohscribe.xsl"):
  
  try:
    xsl = open(xslfile)
    if xsl:
      xslt = xsl.read()
    else:
      msg = "XSLT file `{}' could not be opened.".format(xslfile)
      flash(msg, 'error')
      return
  
    xslt_tree = etree.XML(xslt)
    transform = etree.XSLT(xslt_tree)
  
    xml = open(xmlfile)
    if xml:
      xml_contents = xml.read()
    else:
      msg = "XML file `{}' could not be opened.".format(xmlfile)
      flash(msg, 'error')
      return

    f = io.StringIO(xml_contents)
    doc = etree.parse(f)
    f.close()
    transform = etree.XSLT(xslt_tree)
    result = transform(doc)

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))
  
  return result


# Return a new file name with 'insert' added before the .ext

def make_new_filename(input_file_name, insert):
  name, ext = os.path.splitext(input_file_name)
  return "{name}-{insert}{ext}".format(name=name, insert=insert, ext=ext)


# IOH now treats an underscore here as indication of a language, like _english, so change any/all underscores to dashes!

def get_IOH_filename(input_file_name):
  
  input_file_name.replace("_", "-")
  parts = os.path.split(input_file_name)
  return parts[0] + "/IOH-" + parts[1]



# Actions here.
# ------------------------------------------------------------


def do_cleanup(filename):
  
  flash("Now inside the do_cleanup function.", 'info')
  
  filepath = "{0}/{1}".format(app.config['UPLOAD_FOLDER'], filename)
  flash("Attempting to open '{}'.".format(filepath), 'info')
  result = "Process is incomplete!"

  clean = make_new_filename(filepath, 'clean')
  pretty = make_new_filename(filepath, 'pretty')

  try:
    with open(filepath, 'r') as xmlfile:
      msg = "File '{}' is open!".format(filename)
      flash(msg, 'info')
    
      if xmlfile.name.rsplit(".")[-1] != "xml":
        msg = "File name must have a .xml extension!"
        flash(msg, 'error')
        return redirect(url_for('main'))
      else:
        msg = "File '{}' does have a .xml extension!".format(filename)
        flash(msg, 'info')

      with open(clean, 'w+') as cleanfile:
        msg = "File '{}' is open!".format(clean)
        flash(msg, 'info')

        counter = 0
        for line in xmlfile:
          cleaned = sanitize_xml(line)
          if cleaned:
            cleanfile.write(cleaned)
            counter += 1

      # Make it pretty

      with open(clean, 'r') as cleanfile, open(pretty, 'w+') as prettyfile:
        try:
          bs = BeautifulSoup(xmlfile, 'lxml')
          prettyfile.write(bs.prettify( ))
        except:
          msg = "Unexpected error: {}".format(sys.exc_info()[0])
          flash(msg, 'error')
          return redirect(url_for('main'))
        
    # parser = etree.XMLParser(resolve_entities=False, strip_cdata=False)
    # document = etree.parse(filepath, parser)
    # document.write(filepath, pretty_print=True, encoding='utf-8')

    flash("XML pretty-print has been applied in '{}'.".format(pretty), 'info')

    result = "Clean-up and pretty-printing are complete. {0} lines of '{1}' were processed to create '{2}'.".format(counter, filename, pretty)

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))

# except IOError:
#     msg = "File '{0}' could not be opened!  Make sure you are picking files ONLY from the '{1}' data " \
#         "directory!".format(filename, app.config['UPLOAD_ALIAS'])
#     flash(msg, 'error')
#     return redirect(url_for('main'))

  return result


def do_transform(filename):
  
  flash("Now inside the do_transform function.", 'info')
  
  filepath = "{0}/{1}".format(app.config['UPLOAD_FOLDER'], filename)
  flash("Attempting to open '{}'.".format(filepath), 'info')
  result = "Process is incomplete!"

  try:
    with open(filepath, 'r+') as xmlfile:
      msg = "File '{}' is open!".format(filename)
      flash(msg, 'info')

      # Now transform it
      IOH_xml = xsl_transformation(xmlfile)
      if IOH_xml is None:
        msg = "Error transforming file `{}'.".format(xmlfile)
        flash(msg, 'error')
        return msg

      output_file_name = get_IOH_filename(xmlfile)

      ioh_file = open(output_file_name, "w")
      if ioh_file:
        ioh_file.write(str(IOH_xml))
        ioh_file.close()
        msg = "Output is in {}".format(output_file_name)
        flash(msg, 'info')
        result = msg

      else:
        msg = "File `{}' could not be opened for output.".format(output_file_name)
        flash(msg, 'error')
        result = msg

  # except IOError:
  #   msg = "File '{0}' could not be opened!  Make sure you are picking files ONLY from the '{1}' data directory!".format(filename, app.config['UPLOAD_ALIAS'])
  #   flash(msg, 'error')
  #   return redirect(url_for('main'))

  except:
    msg = "Unexpected error: {}".format(sys.exc_info()[0])
    flash(msg, 'error')
    return redirect(url_for('main'))

  return result
