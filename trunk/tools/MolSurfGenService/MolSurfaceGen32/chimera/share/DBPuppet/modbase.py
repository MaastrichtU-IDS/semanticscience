# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: modbase.py 28783 2009-09-10 23:02:36Z pett $

import chimera
import  sys, tempfile, os.path
import DBPuppet
import xml.sax

def printMsg(msg):
    sys.__stdout__.write("%s\n" % msg)
    sys.__stdout__.flush()

def handle_file(file_loc):
    if isinstance(file_loc, str): 
        f = open(file_loc, 'r')
        parse_file_sax(f)
    elif isinstance(file_loc, file):
        parse_file_sax(file_loc)

def openInChimera(local_files, remote_files):
    import chimera

    #printMsg("in openInChimera, opening %s %s" % (local_files, remote_files) )

    ##pos use temp files here??

    for l in local_files:
        ## strip the HTML tags from the file
        DBPuppet.stripHTML(l)
        
        ## actually open that file. FINALLY!!!
        chimera.openModels.open("%s" % os.path.abspath(l), noprefs=True )
        
    for r in remote_files:
        chimera.openModels.open("%s" % r, type="PDB", noprefs=True )

        
def parse_file_sax(infile):
    """expects an open file as 'infile'
    this function takes care of closing the handle
    """
    
    from xml.sax import make_parser

    ## instantiate the XML handler
    handler = ModXMLHandler()
    parser = make_parser()
    ## associate the handler with the parser
    parser.setContentHandler(handler)

    #infile = open(file,'r')
    
    ## actually parse the file
    parser.parse(infile)
    infile.close()

    local   = []
    fetch   = []
    
    for data in [handler.getAlignment(), handler.getReference()] + handler.getDerived():
            ## data will be a 2-tuple with containing two strings. The first one is the name of a file
            ## and the second is the URL of that file
    
            ## sometimes, there won't be a URL (and data[1].strip() will be None) if the file can be fetched
            ## from the PDB
        if data[1].strip():
            loc = DBPuppet.getURL(data[1], data[0])
            ## append the name of the file you will write to the 'local' list
            local.append(loc)
        else:
            ## needs to be fetched from the web
            fetch.append("%s" % str(data[0]) )
        
    ## open the files..
    openInChimera(local, fetch)


class ModXMLHandler(xml.sax.handler.ContentHandler):

  """This is a Handler class used to parse the XML files supplied by modbase
  It is completely dependent on a previously decided XML format."""
  

  def __init__(self):
    self.alignment = [None, '']
    self.reference = [None, '']
    self.derived     = []

    self.der_count = 0
    
    self.in_alignment, self.in_reference, self.in_derived = (0,0,0)
    self.loc_elt = 0

  ## this function is always called when a start tag is encountered
  ## it is up to you to determine what tag it is, and do something
  ## accordingly
  def startElement(self, name, attrs):
    if name == "alignment":
      self.in_alignment = 1
      self.alignment[0] = attrs.get("name",'')

    elif name == "reference":
      self.in_reference = 1
      self.reference[0] = attrs.get("name", '') 

    elif name == "derived":
      self.in_derived = 1
      self.derived.append([None,''])
      self.derived[self.der_count][0] = attrs.get("name", '')
      
    elif name == "loc":
      self.loc_elt = 1

  ## function called when an end tag is encountered
  def endElement(self, name):
    if name == "alignment":
      self.in_alignment = 0
    elif name == "reference":
      self.in_reference = 0
    elif name == "derived":
      self.in_derived = 0
      self.der_count = self.der_count + 1
    elif name == "loc":
      self.loc_elt = 0

  ## function called to deal with the information stored between
  ## a start tag and an end tag
  def characters(self, data):      
      if self.in_alignment:
          self.alignment[1] = self.alignment[1] + data
      elif self.in_reference:
          self.reference[1] = self.reference[1] + data
      elif self.in_derived:
          self.derived[self.der_count][1] = self.derived[self.der_count][1] + data

  def getAlignment(self):
    return self.alignment
  def getReference(self):
    return self.reference
  def getDerived(self):
    return self.derived
    
  def printResults(self):
    print "Got:\nALIGNMENT: %s %s\nREFERENCE: %s %s\nDERIVED: %s %s" % \
    (self.alignment[0], self.alignment[1], self.reference[0], self.reference[1], \
     self.derived[0][0], self.derived[0][1] )
