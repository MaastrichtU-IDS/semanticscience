# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: web_demo.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from std_webdata import std_webdata
import chimera.replyobj

from DBPuppet import NO_AUTH, NO_URL
from DBPuppet import getURL, stripHTML

import os

class web_demo(std_webdata):

    def __init__(self):
        import tempfile
        self.demo_dir = tempfile.mkdtemp()

        std_webdata.__init__(self)


    def handle_file(self, file_loc):
        """this function is called from DBPuppet::__init__.py.
        file_loc is either an open file handle, or a string specifying
        the location of the file.
        """

        if isinstance(file_loc, str):
            f = open(file_loc, 'r')
            ## parse the XML
            handler = self.parse_file_sax(f)
        elif isinstance(file_loc, file):
            ## parse the XML
            handler = self.parse_file_sax(file_loc)

        res = self.warnUser()
        if not res:
            self.remove_temp_directory()
            return

        ## this will map name:location
        dloaded_files = {}

        for name,format,url in handler.getWebFiles():
            try:
                loc = getURL(url, name, useTempDir=self.demo_dir)
            except NO_AUTH:
                self.cleanUpDloaded(dloaded_files)
                raise chimera.UserError, "%s: User not authorized to access url %s" % (NO_AUTH, url)

            except NO_URL, what:
                self.cleanUpDloaded(dloaded_files)
                raise chimera.UserError, "%s: %s" % (NO_URL, what)

            if format=='html':
                stripHTML(loc)
            ## add this to the list of downloaded files
            dloaded_files[name] = loc

        ## open the downloaded files, PDB ids, and midas commands in Chimera
        self.open_in_chimera(dloaded_files, handler.getPDBs(), \
                             handler.getAllCmds() )


    def open_in_chimera(self, web_files, pdb_ids, all_cmds):
        import chimera
        from DBPuppet import dangerous

        demo_src_file = None

        for name,loc in web_files.items():
            ## what to do here if it is a .chimerax file??
            if dangerous(loc):
                chimera.replyobj.error( "Not opening requested file: %s" % (loc) )
                self.cleanUpDloaded(os.path.abspath(loc))
                continue
            elif loc.endswith(".src"):
                demo_src_file = loc

        if not demo_src_file:
            raise chimera.UserError, "Couldn't find demo source file (\"*.src\")." \
                  " Can't start demo."

        import Demo
        demo_path = os.path.abspath(demo_src_file)
        started_new = Demo.runDemo( demo_path,
                                    os.path.basename(os.path.dirname(demo_path))
                                    )

        if started_new:
            from Demo import CLOSE_DEMO
            self.cleanup_handler = chimera.triggers.addHandler(CLOSE_DEMO, self.demo_close_cleanup, None)
        else:
            ## need to clean up
            self.remove_temp_directory()

    def demo_close_cleanup(self, triggerName, closure, data):
        self.remove_temp_directory()

        from Demo import CLOSE_DEMO
        chimera.triggers.deleteHandler(CLOSE_DEMO, self.cleanup_handler)

    def remove_temp_directory(self):
        import shutil
        shutil.rmtree(self.demo_dir, ignore_errors=True)



    def warnUser(self):
        ## warn user!
        from DBPuppet import needToWarn
        if needToWarn():

            warning_text = "This file will open a demo in Chimera.\n\n"\
                           "Chimera demos consist of a series of 'steps', "\
                           "with each step comprised of a set of "\
                           "operations executed in Chimera, accompanied by a block "\
                           "of explanatory text presented in a seperate window.\n\n" \
                           "If this demo contains malicious code, opening this file " \
                           "could harm your computer. If you do not trust the source " \
                           "of this demo, you should not open it in Chimera."

            from DBPuppet import WarnUserDialog
            warning_dlg = WarnUserDialog(warning_text)
            res = warning_dlg.run(chimera.tkgui.app)
            if res == 'yes':
                return True
            else:
                return False
        else:
            return True
