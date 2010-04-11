# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: sfld.py 28783 2009-09-10 23:02:36Z pett $

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

def openInChimera(local_files, remote_files, commands):
    import chimera

    for l in local_files:
        ## strip the HTML tags from the file
        #DBPuppet.stripHTML(l)
        
        ## actually open that file. FINALLY!!!
        chimera.openModels.open("%s" % os.path.abspath(l), noprefs=True )
        
    for r in remote_files:
        chimera.openModels.open("%s" % r, type="PDB", noprefs=True )
        
    for c in commands:
        DBPuppet.doMidasCommand(str(c))
                    
def parse_file_sax(infile):
    """expects an open file as 'infile'
    this function takes care of closing the handle
    """

    from xml.sax import make_parser

    ## instantiate the XML handler
    handler = SFLDXMLHandler()
    parser = make_parser()
    ## associate the handler with the parser
    parser.setContentHandler(handler)

    #infile = open(file,'r')
    
    ## actually parse the file
    parser.parse(infile)
    infile.close()

    local   = []
    fetch   = []
    cmds    = []
    
    struct = handler.getStructure()
    if struct[1].strip():
        loc = DBPuppet.getURL(struct[1], "%s.pdb" % struct[0])
        ## append the name of the file you will write to the 'local' list
        local.append(loc)
    else:
        fetch.append("%s" % str(struct[0]) )

    cmds = handler.getCmds()
    ## open the files..
    openInChimera(local, fetch, cmds)


class SFLDXMLHandler(xml.sax.handler.ContentHandler):

  """This is a Handler class used to parse the XML files supplied by the sfld
  It is completely dependent on a previously decided XML format."""
  

  def __init__(self):
    self.structure = [None, None]
    self.cmds = []
    self.cmd_count = 0

    self.in_structure, self.in_pycmds, self.in_cmd = (0,0,0)

  ## this function is always called when a start tag is encountered
  ## it is up to you to determine what tag it is, and do something
  ## accordingly
  def startElement(self, name, attrs):
    if name == "structure":
      self.in_structure = 1
      self.structure[0] = attrs.get("name", '')
      self.structure[1] = attrs.get("loc", '' )
    elif name == "pyCommands":
      self.in_pycmds = 1
    elif name == "cmd":
        self.in_cmd = 1
        self.cmds.append('')
      
  ## function called when an end tag is encountered
  def endElement(self, name):
    if name == "structure":
      self.in_structure = 0
    elif name == "pyCommands":
      self.in_pycmds = 0
    elif name == "cmd":
      self.in_cmd = 0  
      self.cmd_count = self.cmd_count + 1
      
  ## function called to deal with the information stored between
  ## a start tag and an end tag
  def characters(self, data):      
      if self.in_cmd:
          self.cmds[self.cmd_count] = self.cmds[self.cmd_count] + data

  def getStructure(self):
    return self.structure
  def getCmds(self):
    return self.cmds

