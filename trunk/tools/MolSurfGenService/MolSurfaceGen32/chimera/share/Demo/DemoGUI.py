import Demo

from chimera import WizShell
import Tkinter, Pmw
from chimera.HtmlText import HtmlText
import Midas
import chimera
from chimera import CLOSE_SESSION
from Demo import CLOSE_DEMO
from DemoEditor import DemoEditor
from chimera.update import checkForChanges
import os
import time


class DemoGUI(WizShell.WizShell):

    """This class defines a graphical user interface to be
    used for navigating through demos within Chimera.
    
    Each panel in a DemoGUI represents a seperate step in the
    corresponding demo. Clicking 'Next' proceeds to the next panel
    and executes all related Midas commands. Depending on the
    content of the demo, some steps will allow you to click
    'Back', reverting back to the last step (this is reflected
    both in the text in the DemoGUI and in the state of the
    Chimera session.)

    The 'AutoRun' button cycles through each panel, with a
    predetermined delay in between each step
    """

    ## use all the WizShell buttons (Back, Next, Cancel)
    ## plus 'AutoRun'

    buttons = ('Next', 'Back', 'Close')
    help    = "ContributedSoftware/demos/demos.html"

    def __init__(self, demo):
        """'demo' is an instance of a ChimeraDemo object. It contains
        all the necessary information to conduct a demo.
        """

        self.demo = demo
        self.num_steps = demo.getNumSteps()
       
        self.demo_title = self.demo.getTitle()

        ## the delay, in milliseconds, to wait between each panel in 'AutoRun'
        ## mode
        self.global_auto_delay = 0
        self.current_auto_delay = 0

        delay = self.demo.getAutoDelay()
        if delay == 0:
            ## not specified in demo.src file. Use default.
            self.global_auto_delay = 5000 ## 5000ms == 5s
        else:
            self.global_auto_delay = delay * 1000
        

        self.saved_positions = []

        ## remember all models that were already opened before the demo 
        ## was started s.t. when the demo is closed, it will only close 
        ## models that it is responsible for opening....
        self._openModelsOnStart = chimera.openModels.list()

        self._openExtsOnStart = chimera.extension.manager.instances[:]
        #from MultAlignViewer.MAViewer import MAViewer
        #em=chimera.extension.manager
        #for i in em.instances:
        #    if isinstance(i, MAViewer):
        #        self._openMAVOnStart.append(i)

        ## keep a reference to this directory, because will cd here when executing
        ## midas commands
        import os.path
        thisfile = os.path.abspath(__file__)
        thisdir  = os.path.split(thisfile)[0]
        self.demoDataDir  = demo.getDirectory()

        if demo.getImageSrc():
            img_src = os.path.join(self.demoDataDir, demo.getImageSrc())

            if demo.getImageBgColor():
                bg_color = demo.getImageBgColor()
            else:
                bg_color = None
            
        else:
            img_src  = os.path.join(thisdir, "chimera_icon_long.png")
            bg_color = 'black'
        


        ## use a panel size of 200 x 200, all it will contain is text
        WizShell.WizShell.__init__(self, self.num_steps, 200, 200,
                                   img_src, img_bg_color=bg_color)

        ## splice out the '_' from the demo name. nice_name is what we will
        # actually title this demo. This is needed because of wierdness on
        # some filesystems with spaces in file names, and currently, the demo
        # name is derived from the directory in which it resides
        nice_name = ' '.join(self.demo_title.split("_"))

        #############################
        #cycle_img_loc=os.path.join(thisdir, "cycle.gif")
        #cycle_img = Tkinter.PhotoImage(file=cycle_img_loc, master=self.panelFrame)
        #cycle_lbl = Tkinter.Label(self.panelFrame, text="stupid", image=cycle_img)
        #cycle_lbl.pack(side='top', anchor='ne')
        ###############################

        for n in range(self.num_steps):
            panel_title = self.demo.getPanelTitle(n+1)
            if panel_title:
                self.createTitle(n,panel_title)
            else:
                self.createTitle(n, nice_name)

            #num_lbl = Tkinter.Label(self.pInterior(n),
            #                        text="%d of %d" % ((n+1),self.num_steps),
            #                        font=smallFont
            #                        )
            #num_lbl.pack(side='bottom', anchor='e', pady=6, padx=10)

            txt = Pmw.ScrolledText(self.pInterior(n),
                                   text_pyclass = HtmlText,
                                   text_relief = 'flat',
                                   text_wrap = 'word',
                                   text_height=8,
                                   text_width=50
                                   )

            txt.settext(demo.getDemoText(n+1))
            txt.pack(side='top', anchor='nw', fill='both', expand=True, pady=5, padx=20)
            txt.configure(text_state='disabled', hscrollmode='dynamic', vscrollmode='dynamic',
                          text_background=self.pInterior(n).cget('background'))

    
        ## at startup, need to execute any commands that are supposed to happen
        ## during the first panel
        start_cmds = self.demo.getDemoCmds(1)

        cwd = os.getcwd()
        os.chdir(self.demoDataDir)
        self._closeSessionHandler = None
        try:
            self.doSeveralMidasCommands(start_cmds)
        finally:
            os.chdir(cwd)

            self.save_position( "demo_p%s_pos" % (self.getCurrentPanel()+1) )

            ad = self.demo.getStepAutoDelay(self.getCurrentPanel()+1)
            if ad:
                self.current_auto_delay = ad * 1000
            else:
                self.current_auto_delay = self.global_auto_delay

            if self.isLastPanel() and not self.loopVar.get():
                self.controlsMenu.entryconfigure('Auto', state='disabled')

            self._closeSessionHandler = chimera.triggers.addHandler(CLOSE_SESSION, self.Close, None)

            if self.demo.getAutoRunOnStart():
                ## here, we need to do make it look as if the demo is in AutoRun mode,
                ## although it won't actually be so until 'AutoRun' is called
                self.autoVar.set(1)
                self.AutoRun(doNext=False)
                self.auto_handle = chimera.tkgui.app.after(self.current_auto_delay, self.Next)


    def fillInUI(self, parent):
        self.makeCounterMenu(parent)
        from chimera.tkgui import aquaMenuBar
        aquaMenuBar(self.menuBar, parent, pack = True)

        WizShell.WizShell.fillInUI(self, parent)

    def makeCounterMenu(self, parent):
        #navMenuButton = Tkinter.Menubutton(self.countFrame,
        #                                   textvariable = self.panelCountVar,
        #                                   font=self.small_font)

        top = parent.winfo_toplevel()
        self.menuBar = Tkinter.Menu(top, relief='groove', type="menubar", tearoff=False)

        top.config(menu=self.menuBar)
        
        ## File Menu
        self.fileMenu = Tkinter.Menu(self.menuBar)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.fileMenu.add_command(label="Save Demo As...",command=self.saveDemoAs)
        self.fileMenu.add_command(label="Close Demo", command=self.Close)
        self.fileMenu.add_command(label="Open in Editor",
                             command = lambda : DemoEditor(self.getDemo().getSrcText())
                             )



        ## Controls Menu
        self.controlsMenu = Tkinter.Menu(self.menuBar)
        self.menuBar.add_cascade(label="Controls", menu=self.controlsMenu)

        self.loopVar = Tkinter.IntVar(self.controlsMenu)
        self.autoVar = Tkinter.IntVar(self.controlsMenu)

        self.controlsMenu.add_checkbutton(label="Auto", variable = self.autoVar, command=self.AutoRun)
        self.controlsMenu.add_checkbutton(label="Loop", variable = self.loopVar, command=self.loopCB)
        self.controlsMenu.add_separator()
        self.controlsMenu.add_command(label="Next", command = self.Next)
        self.controlsMenu.add_command(label="Back", command = self.Back)

        
        #navMenu.add_checkbutton(label="Auto", )
        #self.loopVar = Tkinter.IntVar(self.countFrame)
        #navMenu.add_checkbutton(label="Loop", variable=self.loopVar)
        #navMenuButton.configure(menu=navMenu)

        #self.panelCountLabel.pack_forget()
        #navMenuButton.pack(side='right', padx=10, pady=5)

    def setNextNavState(self, new_state):
        self.buttonWidgets['Next'].configure(state = new_state)
        self.controlsMenu.entryconfigure('Next', state = new_state)

    def Next(self):
        """Override WizShell's 'Next' function, because we need to actually execute Midas
        commands when the 'Next' button is pushed.
        """
        import os

        pos_cmd = "demo_p%s_pos" % (self.getCurrentPanel()+1)
        self.doMidasCommand("reset %s; wait 1" % pos_cmd)

        ## call WizShell.Next to advance to the next panel. This shows the text for the
        ## next panel, although this may temporarily not correspond to what is shown in the graphics
        ## window for a brief period of time, while the commands are executed.... 
        if self.isLastPanel() and self.loopVar.get():
            ## this function should never be called from the last panel if loopVar isn't set,
            ## because the 'Next' button will have been disabled
            self.closeOpenedModels()
            self.forgetPositions()
            WizShell.WizShell.Restart(self)
        else:
            WizShell.WizShell.Next(self)

        ad = self.demo.getStepAutoDelay(self.getCurrentPanel()+1)
        if ad:
            self.current_auto_delay = ad * 1000
        else:
            self.current_auto_delay = self.global_auto_delay
        
        # get a list of commands that need to be executed when this panel is shown
        # +1 because the Demo maps are 1-indexed
        cmds = self.demo.getDemoCmds(self.getCurrentPanel() + 1)

        # get the current directory
        cwd = os.getcwd()
        ## change to the demo data dir
        os.chdir(self.demoDataDir)

        try:
            self.doSeveralMidasCommands(cmds)        
        finally:
            ## change back to the original directory
            os.chdir(cwd)
            self.save_position( "demo_p%s_pos" % (self.getCurrentPanel()+1) )

            #print "NOW, auto_delay IS %s" % self.current_auto_delay

            if self.isLastPanel():

                if self.loopVar.get():
                    ## parent class automatically makes 'Next' button on last panel
                    ## cancel dialog, want to override this here..
                    self.buttonWidgets['Next'].configure(text="Next",
                                                         command = self.Next) 
                else:
                    ## disable 'Next' button, and re-make it say 'Next'
                    ## (will say finish b/c of WizShell default
                    self.buttonWidgets['Next'].configure(text="Next")
                    self.setNextNavState('disabled')

                    ## disable Auto menu entry (can't turn it on in last panel
                    ## if loop is not set
                    self.controlsMenu.entryconfigure('Auto', state='disabled')

                if self.autoVar.get():
                    ## in autorun mode, and on the last panel. here, we should turn autorun
                    ## mode off, disable the autorun button, re-enable the next button (will
                    ## say 'finish', and enable the 'back' button if necessary

                    ## automatically turn off autorun
                    if not self.loopVar.get():
                        ## turns checkbutton off
                        self.autoVar.set(0)
                    else:
                        ## intent is to loop..
                        self.setBackNavState('disabled')
                        
                        try:
                            chimera.tkgui.app.after_cancel(self.auto_handle)
                        except:
                            pass
                        self.auto_handle = chimera.tkgui.app.after(self.current_auto_delay, self.Next)
                else:
                    ## if the current panel has undo functions, enable the 'Back' button
                    if self.demo.hasUndos(self.getCurrentPanel() + 1) and (not self.isFirstPanel()):
                        self.setBackNavState('normal')
                    else:
                        self.setBackNavState('disabled')

            else:
                if self.autoVar.get():
                    ## in autorun mode, but not on the last panel, just make sure
                    ## the back button is disabled, and register an after to advance
                    ## to the next panel
                    self.setBackNavState('disabled')
                    
                    try:
                        chimera.tkgui.app.after_cancel(self.auto_handle)
                    except:
                        pass
                    
                    self.auto_handle = chimera.tkgui.app.after(self.current_auto_delay, self.Next)
                else:
                    ## if the current panel has undo functions, enable the 'Back' button
                    if self.demo.hasUndos(self.getCurrentPanel() + 1) and (not self.isFirstPanel()):
                        self.setBackNavState('normal')
                    else:
                        self.setBackNavState('disabled')
                        
            
            ##################################
            #if self.autorun_on:
            #    if self.isLastPanel():
            #       
            #    else:
            #      
            #
            #else: ## autorun is *not* on
            #    if self.isLastPanel():
            #        
            ###############################

    def setBackNavState(self, new_state):
        self.buttonWidgets['Back'].configure(state = new_state)
        self.controlsMenu.entryconfigure('Back', state = new_state)

    def Back(self):
        """Override WizShell's 'Back' function, because we [possibly ] have to execute Midas
        commands when the 'Back' button is pushed.
        """
        ## figure out what needs to be done to 'undo' the current state
        undos = self.demo.getDemoUndos(self.getCurrentPanel() + 1)

        ## this should never happen, because the back button, will not
        ## get enabled if there are no undos, but just in case...
        if undos == None:
            undos = []

        
        cwd = os.getcwd()
        os.chdir(self.demoDataDir)
        try:
            self.doSeveralMidasCommands(undos)
        finally:
            os.chdir(cwd)

            ## reset to the position of the models after all commands in the
            ## last panel were executed
            pos_cmd = "demo_p%s_pos" % ( (self.getCurrentPanel()+1)-1 )
            self.doMidasCommand("reset %s; wait 1" % pos_cmd)

            ## call WizShell.Back
            WizShell.WizShell.Back(self)

            ## don't really need to resave this, do I?? 
            #self.save_position( "demo_p%s_pos" % (self.getCurrentPanel()+1) )

            ## now that you're on the previous panel,
            ## if *it* can't be undone or it is the first panel, disable the 'Back' button
            ## else enabled it
            if (not self.demo.hasUndos(self.getCurrentPanel() + 1)) or self.isFirstPanel():
                self.setBackNavState('disabled')
            else:
                self.setBackNavState('normal')

            if self.getCurrentPanel()+1 == self.demo.getNumSteps()-1:
                ## this is the second to last panel, need to re-enable
                ## auto run and Next
                self.controlsMenu.entryconfigure('Auto', state='normal')
                self.setNextNavState('normal')
                
            

    def Close(self, triggerName=None, closure=None, data=None):
        """This function will be called when dialog is dismissed, or demo is
        finished. Close everything and stop all motion.
        """
    
        self.closeOpenedModels()

        try:
            chimera.tkgui.app.after_cancel(self.auto_handle)
        except:
            pass

        WizShell.WizShell.Close(self)
        Demo.demoCancel(self)

        self.forgetPositions()

	if self._closeSessionHandler != None:
            chimera.triggers.deleteHandler(CLOSE_SESSION, self._closeSessionHandler)
	    self._closeSessionHandler = None
        
        chimera.triggers.activateTrigger( CLOSE_DEMO, self.getTitle() ) 


    def closeOpenedModels(self):
        self.doMidasCommand("freeze")

        em = chimera.extension.manager

        for ext_inst in [i for i in em.instances if not i in self._openExtsOnStart][:]:
            if hasattr(ext_inst, "emQuit") and callable(getattr(ext_inst,"emQuit")):
                try:
                    getattr(ext_inst, "emQuit")()
                except:
                    pass
            
        chimera.openModels.close(
            [m for m in chimera.openModels.list() if not m in self._openModelsOnStart]
            )

    def forgetPositions(self):
        for pos in self.saved_positions:
            try:
                self.doMidasCommand("~savepos %s" % pos)
            except:
                pass
    

    def loopCB(self):

        if self.isLastPanel():
            if self.loopVar.get():
                self.controlsMenu.entryconfigure('Auto', state='normal')
                self.setNextNavState('normal')
                self.buttonWidgets['Next'].configure(command = self.Next)
            else:
                self.controlsMenu.entryconfigure('Auto', state='disabled')
                self.setNextNavState('disabled')
                self.buttonWidgets['Next'].configure(command = self.Close)


    def AutoRun(self, doNext=True):
        """This function will be called when the 'AutoRun' button is pushed.
        """

        ## if you're not already in AutoRun mode...
        if self.autoVar.get():
            
            ## when in AutoRun mode, user is not able to click 'Next' or 'Back'
            self.setNextNavState('disabled')
            self.setBackNavState('disabled')

            step_auto_delay = self.demo.getStepAutoDelay(self.getCurrentPanel()+1)
            if step_auto_delay and step_auto_delay != 0:
                self.current_auto_delay = step_auto_delay * 1000
            else:
                self.current_auto_delay = self.global_auto_delay
            
            ## based on current panel, determine what next function should do,
            ## and schedule an 'after' callback
            if doNext:
                self.Next()
            

        ## you are already in AutoRun mode, and the user pressed the 'Stop AutoRun'
        ## button
        else:
            ## cancel the callback
            chimera.tkgui.app.after_cancel(self.auto_handle)

            ## enable 'Next' button
            self.setNextNavState('normal')
            
            ## if the current panel has undo commands, enable 'Back'
            if self.demo.hasUndos(self.getCurrentPanel() + 1) and (not self.isFirstPanel()):
                self.setBackNavState('normal')

            if self.isLastPanel() and not self.loopVar.get():
                self.controlsMenu.entryconfigure('Auto', state='disabled')
            

    def doSeveralMidasCommands(self, cmds):
        """ just wraps 'doMidasCommand', but takes care of disabling 'Next'
        and 'Back' buttons s.t. user doesn't click 'Next' while commands
        for a certain panel are still executing...
        """

        ## save the state of the 'Next' button and disable it
        cur_next_state = self.buttonWidgets['Next'].cget("state")
        self.setNextNavState('disabled')
        
        ## save the state of the 'Back' button and disable it
        cur_back_state = self.buttonWidgets['Back'].cget("state")
        self.setBackNavState('disabled')

        ## save the state of the 'AutoRun' button and disable it
        cur_auto_state = self.controlsMenu.entrycget('Auto',"state")
        self.controlsMenu.entryconfigure('Auto', state='disabled')
        

        ## do the commands
        try:
            for cmd in cmds:
                self.doMidasCommand(cmd)
            #finish ongoing motions:
            self.doMidasCommand("wait")
        finally:
            ## restore button states...
            self.setNextNavState(cur_next_state)
            self.setBackNavState(cur_back_state)
            
            self.controlsMenu.entryconfigure('Auto', state=cur_auto_state)
        

    def doMidasCommand(self, cmd):
        """ 'cmd' is the text of a Midas command
        This function will execute 'cmd'  using the Midas command line
        """

        from Midas import midas_text
        
        #code = None

        try:
            #code = Midas.midas_text.makeCommand(cmd)
	    if midas_text.makeCommand(cmd):
		    Midas.wait(1)
        except IOError, v:
            raise "Can't make command from %s" % cmd, v

        #if code is not None:
        #    try:
        #        exec code
        #        Midas.wait(1)
        #    except IOError, v:
        #        from chimera import replyobj
        #        replyobj.error("Error occured when executing midas command %s: %s" % (cmd, v))


    def getTitle(self):
        return self.demo.getNiceTitle()


    def save_position(self, pos_name):
        self.doMidasCommand("savepos %s" % pos_name)

        try:
            i = self.saved_positions.index(pos_name)
        except ValueError:
            self.saved_positions.append(pos_name)


    def getDemo(self):
        return self.demo


    ##### methods for saving demos ######
    #
    #
    
    def saveDemoAs(self):
        from OpenSave import SaveModeless
        SaveModeless(command=self._saveCB, title="Choose Demo Save Location",
                     dialogKw={'oneshot':1}, historyID="Demo Save As",
                     defaultFilter=0, filters=[("Demo", ["*.src"], ".src")]
                     )

    def _saveCB(self, okayed, dialog):
        if okayed:
            for path in dialog.getPaths():
                self.saveDemo(path)

    def saveDemo(self, dest_demo_file):
        import chimera.replyobj
        
        import glob, os.path, shutil

        dest_demo_dir = os.path.dirname(dest_demo_file)    

        current_demo_dir = self.getDemo().getDirectory()
        current_demo_src = self.getDemo().getSrcText()

        all_files  = glob.glob( os.path.join(current_demo_dir, '*') )
        demo_files = self.searchForFilenames(self.getDemo(), all_files) 

        for f in demo_files + [current_demo_src]:
            if f == current_demo_src:
                dest_path = dest_demo_file
            else:
                dest_path = dest_demo_dir 

            try:
                shutil.copy(f, dest_path)
            except IOError, what:
                raise chimera.UserError,  "Error while writing file:\n%s\n" % what

        chimera.replyobj.status("Successfully saved demo '%s' (and all associated data) to %s\n"
                                % ( self.getTitle(), dest_demo_file )
                                )

    def searchForFilenames(self, demo, fname_list):
        """looks at all the commands in 'demo' to see which of the
        files in 'fname_list' are mentioned. returns a subset of
        that list"""

        import os.path

        ## get a list-- each elt is a list of commands for that step
        step_cmds = [p.getCmds() for p in demo.demoPanels.values()]

        import operator
        all_steps  = reduce(operator.add, step_cmds)
        all_cmds   = reduce(operator.add, [cmd.split(";") for cmd in all_steps])

        found_fnames = []

        for fn in fname_list:
            for c in all_cmds:
                if c.find(os.path.basename(fn))>=0 and c.find("open")>= 0:
                    found_fnames.append(fn)
                    break

        return found_fnames
