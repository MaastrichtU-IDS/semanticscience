# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: send_to_chimera.py 26655 2009-01-07 22:02:30Z gregc $

import sys

class FileLock:
    def __init__(self):
        pass
    
    def lock(self, file_obj):

        fd = file_obj.fileno()
        
        if sys.platform=='win32':
            current_pos = file_obj.tell()
            file_obj.seek(0)

            import msvcrt
            try:
                msvcrt.locking(fd, msvcrt.LK_LOCK, 1000)
            except IOError, what:
                print "unable to lock file %s: %s" % (file_obj.name, what)

            file_obj.seek(current_pos)

        else:
            import fcntl
            if file_obj.mode == 'w' or file_obj.mode == 'a':
                fcntl.lockf(fd, fcntl.LOCK_EX)
            elif file_obj.mode == 'r':
                fcntl.lockf(fd, fcntl.LOCK_SH)
        
    def unlock(self, file_obj):

        fd = file_obj.fileno()

        if sys.platform == 'win32':
            current_pos = file_obj.tell()
            file_obj.seek(0)

            import msvcrt
            try:
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1000)
            except IOError, what:
                print "unable to lock file %s: %s" % (file_obj.name, what)
            
            file_obj.seek(current_pos)

        else:
            import fcntl
            fcntl.lockf(fd, fcntl.LOCK_UN)


def getWebFile():
  import sys, os, tempfile
  try:
    # try USER first because cygwin rewrites USERNAME to user's full name
    username = os.environ["USER"]
  except KeyError:
    # Windows
    username = os.environ["USERNAME"]

  web_file = "chim_webinfo-%s" % username
  web_path = os.path.join(tempfile.gettempdir(), web_file)

  if not os.path.exists(web_path):
    #print "can't find web info file, starting new chimera.."
    return None
  
  try:
    f = open(web_path, 'r')
  except IOError, what:
    if what.errno == 13: ##don't have permission to open key file
      #print "Not Authorized", \
      #		      "You are not authorized to send information to Chimera!"
      return None

  #from FileLock import FileLock
  fl = FileLock()
  fl.lock(f)
  del fl

  return f
    
def determineKeys(winfo_file):  

  key_string = winfo_file.readline()
  #winfo_file.close()

  if not key_string or (len(key_string.split()) != 3):
    #print "couldn't find well-formed key, exiting..."
    return ''
  else:
    return key_string.strip()

def determinePortNumbers(winfo_file):
  
  port_entries = winfo_file.readlines()
  #winfo_file.close()

  if len(port_entries) <= 1:
    #print "no available ports in webinfo file, exiting..."
    return []

  ## get just port entries, not keys
  available_ports = port_entries[1:]
  available_ports = [p.split(",")[0] for p in available_ports]
  available_ports = [int(p) for p in available_ports]
  available_ports.reverse()
  
  return available_ports




def generate_input_file(path):
  import input_code

  import tempfile
  (file, loc) = tempfile.mkstemp()
  f = open(loc, 'w')

  #mod_path = "\\\\".join(path.split("\\"))
  
  f.write(input_code.parse_code % (path, path) + "\n")
  f.close()

  return loc

def verify_connection(socket_f, keys):
  ##establish that it is indeed chimera that you are talking to.
  verify = socket_f.readline()
  
  if not verify.strip()=="CHIMERA":
    #print "not talking to Chimera!!, got %s instead!" % verify
    #socket_f.close()
    #del socket_f
    return False
  
  ## read the 'keys' from the file. This is an authentication mechanism.
  ## if this was coming from a different computer or different user than
  ## chimerea was running on, you would be unable to open up the keyfile
  ## (because we made it user-only r/w)
  #print "sendalling KEYS: *%s*" % keys
  
  ## send the key over. If it is the wrong key, chimera will break
  ## the socket connection
  socket_f.write("%s\n" % keys)
  socket_f.flush()

  key_ok = socket_f.readline()
  #print "got **%s** for key_ok" % key_ok
  if key_ok.strip() == "OK":
    #print "KEY OK"
    return True
  elif key_ok.strip() == "NO":
    #print "oops. sent bad key"
    #socket_f.close()
    return False


def send(path):

  socket_f = get_chimera_socket()
  if socket_f is None:
    start_chimera()
    import time
    for i in range(20):
      socket_f = get_chimera_socket()
      if socket_f is not None:
        break
      time.sleep(3)
    else:
      return 'NO CHIMERA FOUND'

  socket_f.write("%s\n" % path)
  socket_f.flush()
  
  ## don't do anything with this response, but will eventually..
  open_res = socket_f.readline()
  
  ## close the connection
  socket_f.close()
  return 'SENT'


def get_chimera_socket():

  web_file = getWebFile()
  if not web_file:
    return None

  keys = determineKeys(web_file)
  if not keys:
    return None

  web_file.seek(0)
  ports = determinePortNumbers(web_file)

  #from FileLock import FileLock
  fl = FileLock()
  fl.unlock(web_file)

  web_file.close()
  
  s = None
  for p in ports:
    s = socket_to_chimera(p)
    if s:
      break
  else:
    #print "None of the sockets worked...."
    return None

  # Make sure we're really talking to chimera
  socket_f = s.makefile(mode='rw')
  if not verify_connection(socket_f, keys):
    socket_f.close()
    return None
  return socket_f
      

def socket_to_chimera(port):

  ## using Python sockets here..

  import socket
  ## use an internet socket, streaming transport
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  try:
    s.connect(('localhost', port))
  except socket.error, e:
    s.close()
    s = None

  return s


def start_chimera():
  import sys, os.path, subprocess
  prog = os.path.join(os.path.dirname(sys.executable), "chimera")
  pid = subprocess.Popen([prog]).pid


## Start here....
if __name__ == '__main__':
  import sys, os, tempfile
  argc = len(sys.argv)
  
  if argc != 2:
    syntax()

  import os
  
  ## 'path' is the path to an XML file (presumably downloaded from clicking in a link in a browser)

  path = sys.argv[1]

  send(path)
