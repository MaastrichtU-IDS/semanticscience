import chimera
from chimera.baseDialog import ModelessDialog, AskYesNoDialog

_currentDemo=None

class DemoError(Exception):
    pass   # "Error constructing demo from source file"

CLOSE_DEMO = "Close Demo"

def startDemo(demo_name):
    import os.path
    thisfile = os.path.abspath(__file__)
    thisdir  = os.path.split(thisfile)[0]
    script = os.path.join(thisdir, "demos", demo_name, "demo.src")
    runDemo(script, demo_name)

def openDemo(path):
    import os.path
    demo_name = os.path.basename(os.path.dirname(path))
    runDemo(path, demo_name)
    return []

def runDemo(script, demo_name):
    global _currentDemo

    if _currentDemo:
        import tkMessageBox

        ## get some info about the demo user wants to open
        import ChimeraDemo
        try:
            d = ChimeraDemo.ChimeraDemo(script, demo_name)
        except DemoError:
            demo_title = ' '.join( demo_name.split("_"))
        else:
            demo_title = d.getTitle()
            del d
        
        if _currentDemo.demo.getSrcText() == script:
            dlg_msg = "You are already running the demo '%s'.\n\n "  \
                      "Would you like close this demo, and all "     \
                      "associated models, and start over?"           \
                      % _currentDemo.getTitle()
        else:
            dlg_msg = "You already have a demo in progress ('%s').\n\n" \
                      "Would you like to close this demo, and "         \
                      "all associated models, and open up the "         \
                      "'%s' demo?"                                      \
                      % ( _currentDemo.getTitle(), demo_title)

            
        dlg = AskYesNoDialog(dlg_msg, title="Demo in progress",
				help="ContributedSoftware/demos/demos.html")
        res = dlg.run(chimera.tkgui.app)
        #res = tkMessageBox.askquestion(master=chimera.tkgui.app,
        #                               title="Demo in progress",
        #                               message=dlg_msg
        #                               )
        if res == 'yes':
            ## a demo *is* currently running, and user wants to start
            ## this new demo...
            _currentDemo.Cancel()
            d = createDemoFromScript(script, title=demo_name)
            if d:
                _currentDemo = d
                return True
            else:
                return False
        elif res == 'no':
            ## a demo *is* currently running, and user doesn't want
            ## to start this new demo
            return False
            
    else:
        d = createDemoFromScript(script, title=demo_name)
        if d:
            ## no demo is currently running, start this new one...
            _currentDemo = d
            return True
        else:
            return False

def createDemoFromScript(script, title=None):
    import ChimeraDemo, DemoGUI

    try:
        d = ChimeraDemo.ChimeraDemo(script, title)
    except DemoError, what:
        chimera.replyobj.error("%s\n  %s\n" % (DemoError, what) )
        return None
    return DemoGUI.DemoGUI(d)

def chooseDemo():
    from OpenSave import OpenModeless
    OpenModeless(command=_chooseCB, title="Choose Demo File",
                    historyID="Demo", defaultFilter=0,
                    filters=[("Demo", ["*.src"])], dialogKw={'oneshot': 1})

def _chooseCB(okayed, dialog):
    if okayed:
        for path in dialog.getPaths():
            openDemo(path)


def demoCancel(demo_gui):
    global _currentDemo
    _currentDemo = None


def showDemoEditor():
    import DemoEditor#, chimera
    #chimera.dialogs.display(DemoEditor.DemoEditor.name)
    DemoEditor.DemoEditor()


    
class XMLDemo:
    def XMLName(self):
        return "Demo"
    def XMLAttributes(self):
        return {"Demo":[ ('title','title'),
                         ('autodelay','autodelay'),
                         ('image','image'),
                         ('bg_color','bg_color'),
                         ('autorun_on','autorun_on'),
                         ('description','description'),
                         ('datadir', 'datadir')
                         ]}
    def XMLFields(self):
        return {"Panel"    : "panels"}

    def XMLEmbedding(self):
        return {"Panel": XMLPanel}
 
class XMLPanel:
    def XMLName(self):
        return "Panel"
    def XMLAttributes(self):
        return {"Panel":[('autodelay','autodelay'),
                         ('title','title'),
                         ('id','id')
                         ]}
    def XMLFields(self):
        return {"Text"    : "text",
                "Command" : "command",
                "Undo"    : "undo"}
    def XMLEmbedding(self):
        return { "Command": XMLCommand,
                 "Undo"   : XMLUndo }

class XMLCommand:
    def XMLName(self):
        return "Command"
    def XMLAttributes(self):
        return {"Command":[('active','active')]}
    def XMLFields(self):
        return {"CommandItem" : "item"}
    def XMLEmbedding(self):
        return {}

class XMLUndo:
    def XMLName(self):
        return "Undo"
    def XMLAttributes(self):
        return {"Undo":[('active','active')]}
    def XMLFields(self):
        return {"UndoItem" : "item"}
    def XMLEmbedding(self):
        return {}



##### saving ######



class AboutDemosDialog(ModelessDialog):
	"""show information about Demos"""

	name = 'About Demos'
	buttons = ('Close')
	default = 'Close'
        help = "ContributedSoftware/demos/demos.html"

	def fillInUI(self, master):
		from chimera import chimage
                import Tkinter

                import os.path
                thisfile = os.path.abspath(__file__)
                thisdir  = os.path.split(thisfile)[0]
                
		icon = chimage.get( os.path.join(thisdir, 'chimera_icon_small.png'), master)
		l = Tkinter.Label(master, image=icon, borderwidth=10)
		l.__image = icon
		l.pack(side='left')
		lab = Tkinter.Label(master, borderwidth=10, justify='left',
                                    text=
                                    "Demos listed in the Tools menu were made using\n"
                                    "Chimera's Demo feature, which enables the easy\n"
                                    "creation and replay of custom multistep demos.\n"
                                    "Each step is comprised of a set of operations performed\n" 
                                    "in Chimera, and an accompanying block of explanatory text.\n"
                                    "\n"
                                    "For more information on how to create demos, click the Help button.\n"
                                    )
		lab.pack(side='right')

## register dialogs...
from chimera import dialogs
dialogs.register(AboutDemosDialog.name, AboutDemosDialog)

## register file types...
from chimera import fileInfo
fileInfo.register('Chimera demo', openDemo, ['.src'], ['demo'],  \
                  mime=['application/x-demo'], canDecompress=False,
		  category=chimera.FileInfo.SCRIPT)

## add triggers...
chimera.triggers.addTrigger(CLOSE_DEMO)
