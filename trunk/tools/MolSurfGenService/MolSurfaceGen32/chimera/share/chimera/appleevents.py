# -----------------------------------------------------------------------------
# Register handler for Apple events, like data file being dropped on Chimera
# icon, or click on Chimera icon to bring application window to top.
#
def register_apple_event_handler():

    from tkgui import windowSystem
    if windowSystem == 'aqua':
        return     # ArgvCollector2._dooneevent() crashes Chimera on Aqua.

    if not is_display_accessible():
        return

    avc2 = ArgvCollector2()

    AEV_TRIGGER = 'new frame'
    from chimera import triggers
    AEV_tHandler = triggers.addHandler(AEV_TRIGGER, avc2._dooneevent, None)

    def delete_ae_handler(triggerName, handler, data):
        from chimera import triggers
        try:
            triggers.deleteHandler(AEV_TRIGGER, handler)
        except (KeyError, ValueError):
            pass
    # when chimera exits, want to stop checking for Apple Events
    triggers.addHandler("Chimera exit", delete_ae_handler, AEV_tHandler)

# -----------------------------------------------------------------------------
#
from argvemulator import ArgvCollector
from Carbon import AE
import Carbon.AppleEvents as AEc        # Apple Event constants
import Carbon.File as File

class ArgvCollector2(ArgvCollector):

    def __init__(self):
        self.quitting = 0
        self.ae_handlers = {}
        # Remove the funny -psn_xxx_xxx argument
        import sys
        if len(sys.argv) > 1 and sys.argv[1][:4] == '-psn':
            del sys.argv[1]
        ehandlers = ((AEc.kAEOpenApplication, self.open_app),
                     (AEc.kAEOpenDocuments, self.open_file),
                     (AEc.kAEReopenApplication, self.reopen_app),
                     (AEc.kAEQuitApplication, self.quit_app),
                     (AEc.kAEApplicationDied, self.launched_app_died),
                     )
        for etype, cb in ehandlers:
            AE.AEInstallEventHandler(AEc.kCoreEventClass, etype, cb)

    def _dooneevent(self, triggerName, closure, data):
        ArgvCollector._dooneevent(self, timeout=0)

    def open_file(self, requestevent, replyevent):
	from chimera import openModels, UserError, replyobj
        try:
            listdesc = requestevent.AEGetParamDesc(AEc.keyDirectObject,
                                                                AEc.typeAEList)
            for i in xrange(listdesc.AECountItems()):
                aliasdesc = listdesc.AEGetNthDesc(i + 1, AEc.typeAlias)[1]
                alias = File.Alias(rawdata=aliasdesc.data)
                fsref = alias.FSResolveAlias(None)[0]
                pathname = fsref.as_pathname()
                #print "GOT OPEN FOR %s" % pathname
                openModels.open(pathname)
        except UserError, what:
            replyobj.error("%s" % what)
        except:
            import sys, os.path
            replyobj.error(
                    "An unknown error occurred while opening the file '%s': %s"
                    % (os.path.split(pathname)[1], sys.exc_info()[1]))

    def open_app(self, requestevent, replyevent):
        show_chimera()

    def reopen_app(self, requestevent, replyevent):
        show_chimera()

    def quit_app(self, requestevent, replyevent):
        from chimera import dialogs
        dialogs.display("Confirm Exit")

    def launched_app_died(self, requestevent, replyevent):
        # On Mac OS 10.5 this event raises an error on start-up visible in
        # the reply log unless we process it.
        pass

# -----------------------------------------------------------------------------
# Give running Chimera the focus when user clicks on Dock icon or tries
# to relaunch Chimera.
#
def show_chimera():

    from chimera.tkgui import windowSystem, app
    if windowSystem == 'x11':
        #
        # Under X11 the Chimera windows are managed by the X server application.
        # The X11 menus show along the top of the display when Chimera has the
        # focus.  It is necessary to activate the X11 application.
        #
        from os import system
        system("""osascript -e 'activate application "X11"'""")
        #
        # Give focus to and raise the main Chimera window.
        # Without this step other X11 applications might get the focus and
        # obscure the Chimera window.
        #
        app.focus_force()
        app.bringToFront()
        #
        # TODO: Should raise all Chimera windows above other X11 windows.
        #       Preserving window stacking order while doing this is a bit
        #       of trouble.
        #

# -----------------------------------------------------------------------------
# If user is not logged in on console some Mac calls that need access
# to the screen cause an abort() on 10.4.11 but not on 10.5.2.  This
# routine allows checking for access so that abort() can be avoided.
#
def is_display_accessible():

    from ctypes import cdll
    from ctypes.util import find_library
    asl = cdll.LoadLibrary(find_library('ApplicationServices'))
    return asl.CGMainDisplayID() != 0
