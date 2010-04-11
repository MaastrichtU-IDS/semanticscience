import Demo
from Demo import DemoError, XMLPanel, XMLDemo, XMLCommand, XMLUndo
import os.path

from multiloader2 import Multiloader


class Counter:
    def __init__(self, start=None):
        if not start:
            self.count = 0
        else:
            self.count = start
        
    def inc(self):
        self.count = self.count + 1

    def dec(self):
        self.count = self.count - 1

    def get(self):
        return self.count




class DemoPanel:
    """This class represents a panel in a ChimeraDemo"""

    def __init__(self, id):

        self.id = id

        self.text =  ''
        self.title = ''
        self.cmds =  []
        self.undos = None
        self.delay = None


    def setText(self, text):
        self.text = text
    def getText(self):
        return self.text


    def addCmd(self, cmd):
        self.cmds.append(cmd)
    def setCmds(self, cmds):
        self.cmds = cmds
    def getCmds(self, all=False):
        if all:
            return [c[1] for c in self.cmds] 
        else:
            return [c[1] for c in self.cmds if c[0]]


    def addUndo(self, undo):
        self.undos.append(undo)

    def getUndos(self, all=False):
        ## returns None if there are no undos
        ## else return list of undo commands as strings
        ## if there are no undos, but the 'Back' button should
        ## still be enabled, need empty list

        if self.undos == None:
            return None

        else:
            if all:
                return [u[1] for u in self.undos]
            else:
                return [u[1] for u in self.undos if u[0]]

    def setUndos(self, undos):
        self.undos = undos


    def setDelay(self, delay):
        self.delay = delay
    def getDelay(self):
        return self.delay

    def setId(self, id):
        self.id = id
    def getId(self):
        return self.id

    def setTitle(self, title):
        self.title = title
    def getTitle(self):
        return self.title

        
class ChimeraDemo:
    def __init__(self, src_txt, title=None):
        
        if not os.path.isabs(src_txt):
            self.src_txt = os.path.abspath(src_txt)
        else:
            self.src_txt = src_txt

        #self.name = name

        if title:
            self.title = title
        else:
            self.title = 'Chimera Demo'

        ## path to the image file to be used in Demo GUI
        self.img_src = None
        self.img_bg_color = None
        

        self.auto_delay = 0
        self.autorun_on_start = False

        self.description = ''
        self.datadir = None

        self.demoPanels = {}

        self.parseDemoFile(self.src_txt)
        

    def getTitle(self):
        return self.title

    def getNiceTitle(self):
        return ' '.join( (self.getTitle().split("_")))

    def getDescription(self):
        if self.description:
            return self.description
        else:
            return "No description available"

    def getSrcText(self):
        return self.src_txt

    def getImageSrc(self):
        return self.img_src

    def getImageBgColor(self):
        return self.img_bg_color

    def getDataDir(self):
        return self.datadir

    def getAutoRunOnStart(self):
        return self.autorun_on_start

    def getDirectory(self):
	d = self.getDataDir()
        if d:
            return d
        else:
            return os.path.dirname(self.src_txt)

    def getNumSteps(self):
        return len(self.demoPanels)

    def getDemoText(self, num):
        return self.demoPanels[num].getText()

    def getDemoCmds(self, num):
        return self.demoPanels[num].getCmds()

    def getPanelTitle(self, num):
        return self.demoPanels[num].getTitle()

    def getDemoUndos(self, num):
        undos = self.demoPanels[num].getUndos()
        return undos
        #if  undos == None:
        #    return []
        #else:
        #    return undos

    def hasUndos(self, num):
        if self.demoPanels[num].getUndos() == None:
            return False
        else:
            return True
        

    def getAutoDelay(self):
        return self.auto_delay


    def getStepAutoDelay(self, num):
        delay = self.demoPanels[num].getDelay()
        if delay:
            return delay
        else:
            return None

    def openDemoFile(self):
        f = open(self.src_txt, 'r')
        return f


    def parseDemoFile(self, src_path):

        demo_type = None
        
        f = open(src_path, 'r')
        for line in f.readlines():

            if line.find("[INFO")  >= 0 or \
                   line.find("[START") >= 0:
                demo_type = 'old'
                break

            elif line.find("<Demo") >= 0 or \
                     line.find("<Panel") >= 0:
                demo_type = 'new'
                break
        else:
            raise DemoError("Couldn't identify Demo source format")

        if demo_type == 'old':
            from format2065 import DemoParser2065
            demo_parser = DemoParser2065(src_path, self)
            #self.parseOldDemo(src_path)
        else:
            ## demo type is new
            #self.parseNewDemo(src_path)
            demo_parser = DemoParserNew(src_path, self)

        demo_parser.parseDemo()
        f.close()

class DemoParser:
    def __init__(self, src_path, demo_obj):
        self.src_path = src_path
        self.demo     = demo_obj

    def parseDemo(self):
        raise NotImplemented

class DemoParserNew(DemoParser):

    def parseDemo(self):
         m = Multiloader()
         m.load( self.src_path, [XMLDemo])
         objs = m.getObjects()
         #print objs
         demoObjs  = objs['Demo']
         #panelObjs = objs['Panel'] 
         demoObj = demoObjs[0]

         if not demoObj.panels:
             raise DemoError("Couldn't find valid panel description in source file. "
                             "Demo must have at least one step.")

         if hasattr(demoObj, 'title'):
             self.demo.title = str(demoObj.title)
         else:
             self.demo.title = "Chimera Demo"

         if hasattr(demoObj, 'autodelay')  :   self.demo.auto_delay = int(demoObj.autodelay)
         if hasattr(demoObj, 'image')      :   self.demo.img_src   = str(demoObj.image)
         if hasattr(demoObj, 'bg_color')   :   self.demo.img_bg_color = str(demoObj.bg_color)
         if hasattr(demoObj, 'autorun_on') :   self.demo.autorun_on_start = True
         if hasattr(demoObj, 'description'):   self.demo.description = str(demoObj.description)
         if hasattr(demoObj, 'datadir')    :   self.demo.datadir = str(demoObj.datadir)
         
         if isinstance(demoObj.panels, XMLPanel):
             demoObj.panels = [demoObj.panels]
         
         for panel in demoObj.panels:
             p = self.parsePanel(panel)
             self.demo.demoPanels[p.getId()] = p
                      
         #print "ChimeraDemo: %d" % len(demoObjs)
         #print "Panel:       %d" % len(panelObjs)
         
        

    def parsePanel(self, xml_panel):
        p = DemoPanel(int(xml_panel.id))

        if hasattr(xml_panel,'autodelay'):
            p.setDelay( int(xml_panel.autodelay) )

        if hasattr(xml_panel,'title'):
            p.setTitle( str(xml_panel.title) )
        else:
            p.setTitle( self.demo.title )

        ## handle text
        if isinstance(xml_panel.text,list):
            p.setText( str(xml_panel.text[0]) )
        elif isinstance(xml_panel.text, basestring):
            p.setText( str(xml_panel.text) ) 

        ## handle commands
        if isinstance(xml_panel.command, list):
            cmd_list = []
            for c in xml_panel.command:
                cmd_list.append( (str(c.active)=="True", str(c.item)) )    
            p.setCmds( cmd_list )
            
        elif isinstance(xml_panel.command, XMLCommand):
            p.setCmds( [ ( str(xml_panel.command.active)=="True", str(xml_panel.command.item) ) ] )

        ## handle undos
        if isinstance(xml_panel.undo, list):
            undo_list = []
            for u in xml_panel.undo:
                undo_list.append( (str(u.active)=="True", str(u.item)) )    
            p.setUndos( undo_list )
            
        elif isinstance(xml_panel.undo, XMLUndo):
            p.setUndos( [ (str(xml_panel.undo.active)=="True", str(xml_panel.undo.item)) ] )

        return p


    
