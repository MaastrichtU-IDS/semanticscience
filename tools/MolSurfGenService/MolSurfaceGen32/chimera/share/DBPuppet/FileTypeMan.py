# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: FileTypeMan.py 26655 2009-01-07 22:02:30Z gregc $

import sys, os, shutil

if sys.platform == 'win32':
    import _winreg


class FileTypeMan:
    def __init__(self):
        self.platform = sys.platform

        try:
            self.home_dir = os.environ['HOME']
        except KeyError:
            ## probably on windows...won't use this anyway
            pass

    def registerFileAssn(self, desc, exts, mimetype):
        ## description (i.e. "Chimera Web Data"), extension (i.e. ".chimerax"),
        ## MIME-type (i.e. "application/x-chimerax")
        
        if self.platform == 'win32':
                return self.registerForWin(desc, exts, mimetype)

        #elif self.platform == 'darwin':
        #    return self.registerDarwinType(type_desc_list)

        else:
            return self.registerForUnix(desc, exts, mimetype)

    def getCurrentHandler(self, mime_types, exts):
        if self.platform == 'win32':
            ## no support for win32 yet....
            return self.getWinHandler(exts)
        else:
            return self.getUnixHandler(mime_types)


    def getUnixHandler(self, mime_types):

        ## in case the type has more than one mime-type, only use
        ## the first one for now...
        mime_type = mime_types[0]
    
        import mailcap
        caps = mailcap.getcaps()
        match = mailcap.findmatch(caps, mime_type)
       
        if match == (None, None):
            return "<None>"
        else:
            try:
                cmd = match[0]
                exec_path = cmd.split()
                exec_file = os.path.split(exec_path[0])[1]
            except:
                return "<None>"

            if len(exec_path) > 2:
                return exec_file + " " + ' '.join(exec_path[1:-1]) 
            else:
                return exec_file

    def getWinHandler(self, exts):
        
        import _winreg

        ## in case the type has more than one extension,
        ## only use the first one for now...
        ext = exts[0]

        ## first check if it is registered in HKEY_CURRENT_USER.
        ## if not, check to see if there is a system-wide registered
        ## type in HKEY_CLASSES_ROOT
        software_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software", 0, _winreg.KEY_READ)
        classes_key   = _winreg.OpenKey(software_key, "Classes", 0, _winreg.KEY_READ)

        cmd_line = self.findCmdLine(classes_key, ext)
        if cmd_line:
            return cmd_line

        cmd_line = self.findCmdLine(_winreg.HKEY_CLASSES_ROOT, ext)
        if cmd_line:
            return cmd_line
        else:
            return "<None>"
        
            


    def findSubKey(self, root_key, sub_key):
        """return a ref to the sub_key if it exists, None
        if it doesn't"""

        import _winreg

        index = 0
        found_key = False

        try:
            key_ref = _winreg.OpenKey(root_key, sub_key, 0, _winreg.KEY_READ)
        except EnvironmentError:
            return None
        else:
            return key_ref
        
        
    def findCmdLine(self, root_key, ext):

        import _winreg
        
        cmd_line   = ''
        type        = ''

        #print "attempting to find subkey for %s" % ext
        ext_key = self.findSubKey(root_key, ext)
        if not ext_key:
            #print "couldn't find ext key for %s, returning None" % ext
            return None

        try:
            val, regtype = _winreg.QueryValueEx(ext_key, None)
            type = str(val)
        except WindowsError:
            #print "couldn't get val for ext_key, returning None"
            return None

        type_key = self.findSubKey(root_key, type)
        if not type_key:
            #print "couldn't find type key, returning None"
            return None
        
        try:
            shell_key   = _winreg.OpenKey(type_key, "shell", 0, _winreg.KEY_READ)
            open_key    = _winreg.OpenKey(shell_key, "open", 0, _winreg.KEY_READ)
            command_key = _winreg.OpenKey(open_key, "command", 0, _winreg.KEY_READ)
        except WindowsError:
            #print "badly formed \"shell->open->command\" sequence, returning None"
            return None

        try:
            val, regtype   = _winreg.QueryValueEx(command_key, None)
            cmd_line = str(val)
        except WindowsError:
            #print "couldn't get val for command_key, returning None"
            return None
        
        return self.postProcessCmdLine(cmd_line)


    def postProcessCmdLine(self, cmd_line):
        import os.path

        ## assumes there is no spaces in the path name
        args = cmd_line.split()
        cmd_path  = args[0]

        if cmd_path.find(".exe") >= 0:
            return os.path.split(cmd_path.strip("\""))[1] 

        ## possible there was a space in the command path name.
        ## thus, the command pathname must have been quoted.
        ## so get what's between the quotes.
        else:
            start_idx = cmd_line.find("\"")
            end_idx   = cmd_line.find("\"", start_idx+1)
            
            cmd_path = cmd_line[start_idx+1:end_idx]
            #print "for cmd, got ", cmd_path
           
            return os.path.split(cmd_path)[1]
        

       
################################################
## Functions to de-/register on win32 systems ##
################################################

    def deregisterWin32Type(self, desc, exts, mimetypes):

        desc,type,ext,mime  = type_desc_list

        software_key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software", 0, _winreg.KEY_READ)
        classes_key   = _winreg.OpenKey(software_key, "Classes", 0, _winreg.KEY_READ)

        index = 0
        found_type = False
        found_ext  = False


        while 1:
            try:
                k = _winreg.EnumKey(classes_key, index)
            except EnvironmentError:
                break
            else:
                if  k == type:
                    found_type = True
                elif k == ext:
                    found_ext = True

                index += 1

        if found_type:
            ## should delete key and all of its subkeys, but currently there is no _winreg API to do this,
            ## so just don't do anything for now...
            pass
        if found_ext:
                _winreg.DeleteKey(classes_key, ext)

    def registerForWin(self, desc, exts, mime):

        ## did the registration go OK?
        reg_ok = True

        type = ''.join(desc.split(" ")) + "file"

        for ext in exts:
            ext_res = self.registerWinFileExt(type, ext, mime)
            if not ext_res:
                reg_ok = False
                

        cmd = "\"%s\\chimera.exe\" \"--send\" \"%%1\"" % os.path.split(sys.executable)[0]
        type_res = self.registerWinTypeRcrd(desc, type, cmd)
        if not type_res:
            reg_ok = False

        return reg_ok

    def registerWinTypeRcrd(self, desc, type, cmd):

        import _winreg

        try:
            software_key  = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software", 0, _winreg.KEY_READ)
            classes_key   = _winreg.OpenKey(software_key, "Classes", 0, _winreg.KEY_READ)

            fdesc_key =  _winreg.CreateKey(classes_key, type)
            
            _winreg.OpenKey(classes_key, type, 0, _winreg.KEY_SET_VALUE)
            _winreg.SetValue(classes_key, type, _winreg.REG_SZ, desc)
        
            shell_key = _winreg.CreateKey(fdesc_key, "shell")
            open_key  = _winreg.CreateKey(shell_key, "open")
            
            cmd_key   = _winreg.CreateKey(open_key, "command")
            _winreg.OpenKey(open_key, "command", 0, _winreg.KEY_SET_VALUE) 
            _winreg.SetValue(open_key, "command", _winreg.REG_SZ, cmd)

        except EnvironmentError: 
            return False
        else:
            return True

    def registerWinFileExt(self, type, ext, mime):
                
        ## description (i.e. "Chimera Web Data"), type (i.e. "chimeraxfile"), extension (i.e. ".chimerax"),
        ## MIME-type (i.e. "application/x-chimerax")
        

        import _winreg

        try:
            software_key  = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software", 0, _winreg.KEY_READ)
            classes_key   = _winreg.OpenKey(software_key, "Classes", 0, _winreg.KEY_READ)
            
            extension_key = _winreg.CreateKey(classes_key, ext) 
            extension_key = _winreg.OpenKey(classes_key, ext, 0, _winreg.KEY_SET_VALUE)
            _winreg.SetValue(classes_key, ext, _winreg.REG_SZ, type)
            _winreg.SetValueEx(extension_key, "Content Type", 0, _winreg.REG_SZ, mime)

        except EnvironmentError:
            return False
        else:
            return True

#########################
## End win32 functions ##
#########################

    def registerDarwinType(self, type_desc_list):
        pass


######################################################
## Functions to register file types on Unix systems ##
######################################################

    ##This function registers application/x-chimerax as a mime-type
    def writeMime(self, mime_file, mime_type, exts):
        mime_file.write("#mime type added by Chimera\n")
        #mime_file.write("%s %s\n" % (mime_type, ' '.join(exts) ) )
        mime_file.write("%s   %s\n" % (mime_type, ' '.join([ext.lstrip('.') for ext in exts]) ) )
        mime_file.close()

    ##This function associates an application with the application/x-chimerax mime-type 
    def writeMailcap(self, mc_file, mime_type, cmd):
        mc_file.write("#mailcap entry added by Chimera\n")
        mc_file.write("%s;%s\n" % (mime_type, cmd) )
        mc_file.close()

    def fContainsMime(self, mime_file, mime_type, exts):
        """does file at location 'file' contain an entry for the Mime-type 'mime_type'"""
                    
        mime_reg = False
        all_exts = True

        mimetype_lines = mime_file.readlines()
        new_mimetype_lines = mimetype_lines[:]

        mime_file.close()

        for i in range(len(mimetype_lines)):
            line = mimetype_lines[i]

            if line.strip()=='' or line.lstrip()[0]=='#':
                continue

            try:
                line_mt   = (line.split())[0]
                line_exts = (line.split())[1:]
            except IndexError:
                continue
            
            if line_mt == mime_type:
                mime_reg = True

                for ext in exts:
                    if not ext.lstrip(".") in line_exts:
                        new_mimetype_lines[i] = "%s   %s\n" % ( mime_type, ' '.join([ext.lstrip(".") for ext in exts]) )
                        all_exts = False

        if not mime_reg:
            #print "NO MIME REG"
            return False
        elif mime_reg and (not all_exts):
            mimetype_file = open(os.path.join(self.home_dir, ".mime.types"), 'w')
            for m in new_mimetype_lines:
                mimetype_file.write(m)
            mimetype_file.close()

            #print "MIME REG and NOT ALL_EXTS - fixed"
            return True
        elif (mime_reg and all_exts):
            #print "MIME REG and ALL_EXTS"
            return True

    def fContainsMailcap(self, mailcap_file, mime_type, cmd):
        chimerax_reg = False

        mailcap_lines = mailcap_file.readlines()
        mailcap_file.close()

        for i in range(len(mailcap_lines)):
            line = mailcap_lines[i]

            if line.strip()=='' or line.lstrip()[0]=='#':
                continue

            try:
                line_mt  = (line.split(";")[0]).strip()
                line_cmd = (line.split(";")[1]).split()
            except IndexError:
                continue

            if line_mt == mime_type and line_cmd == cmd.split():
                chimerax_reg = True
                break
            elif line_mt == mime_type and line_cmd != cmd.split():
                mailcap_lines[i] = "%s;%s\n" % (mime_type, cmd)
                mailcap_file = open(os.path.join(self.home_dir,".mailcap"), 'w')
                for m in mailcap_lines:
                    mailcap_file.write(m)
                mailcap_file.close()
                chimerax_reg = True
                break

        return chimerax_reg


    def registerUnixMT(self, mime_type, extensions):
        ##check if user has a .mime.types file in their home directory
        mime_exists    = os.access(os.path.join(self.home_dir, ".mime.types"), os.F_OK)

        if not mime_exists:
            try:
                mime_file = open(os.path.join(self.home_dir,".mime.types"), 'w')
                self.writeMime(mime_file, mime_type, extensions)
            except IOError: 
                return False
            
        ##if .mime.types does exist
        else:
            try:
                mime_file = open(os.path.join(self.home_dir,".mime.types"), "r")
            except IOError:
                return False

            if self.fContainsMime(mime_file, mime_type, extensions):
                return True
            else:
                ##not registered yet, add it
                ##create backup, just in case...
                MIME_BACKUP = os.path.join(self.home_dir, ".mime.types.CHBAK")
                try:
                    shutil.copy(os.path.join(self.home_dir, ".mime.types"), MIME_BACKUP)
                except IOError:
                    print "Unable to make backup of .mime.types file"

                ##write new informatino to the mimetypes file
                try:
                    mime_file = open(os.path.join(self.home_dir,".mime.types"), 'a')
                    self.writeMime(mime_file, mime_type, extensions)
                except IOError:
                     return False
        return True

    def registerUnixMC(self, mime_type, cmd):

        ##check if user has a .mailcap file in their home directory
        mailcap_exists = os.access(os.path.join(self.home_dir, ".mailcap"), os.F_OK)
                    
        ##if the ~/.mailcap file doesnt exist
        if not mailcap_exists:
            try:
                mailcap_file = open(os.path.join(self.home_dir,".mailcap"), 'w')
                self.writeMailcap(mailcap_file, mime_type, cmd)
            except IOError:
                return False
            
        else: ##~/.mailcap does exist
            ##check to see if application/x-chimerax has associated application
            try:
                mailcap_file = open(os.path.join(self.home_dir,".mailcap"), 'r')
            except IOError:
                return False
            
            chimerax_reg = self.fContainsMailcap(mailcap_file, mime_type, cmd)

            if chimerax_reg:
                ##yes it has already been associated
                return True
            else:
                ##nope, write to the pre-existing file
                ##create abckup, just in case..
                MCAP_BACKUP = os.path.join(self.home_dir, ".mailcap.CHBAK")
                print "creating backup of .mailcap file in %s" % MCAP_BACKUP
                try:
                    shutil.copy(os.path.join(self.home_dir, ".mailcap"), MCAP_BACKUP)
                except IOError:
                    print "Unable to make backup of .mailcap file"
                ##write new information to the mailcap file

                try:
                    mailcap_file = open(os.path.join(self.home_dir,".mailcap"), 'a')
                    self.writeMailcap(mailcap_file, mime_type, cmd)
                except IOError:
                    return False
        return True

    def registerForUnix(self, desc, exts, mime):
        
        mime_reg_ok  = self.registerUnixMT(mime, exts)
        if not mime_reg_ok:
            return False

        ## take this out for now, 
        #cmd = os.path.join(os.path.split(sys.executable)[0] , "chimera") + " --send %s"

        ## use the chimera_send script which explicitly passes the '--send' flag to chimera
        cmd = os.path.join(os.path.split(sys.executable)[0] , "chimera_send") + " %s"

        mc_reg_ok = self.registerUnixMC(mime, cmd) 
        if not mc_reg_ok:
            return False

        return True

###########################
## End Unix functions... ##
###########################
