import Tkinter, Pmw
from chimera import chimage
from chimera import tkoptions

import glob, os, os.path, sys, string

import Demo
from Demo.EntryStack import EntryStack
from Demo import DemoError
from Demo import ChimeraDemo, XMLDemo, XMLPanel, XMLCommand, XMLUndo
from ChimeraDemo import DemoPanel

from chimera.HtmlText import HtmlText,  HtmlParseError
from chimera import help, UserError, dialogs
from chimera.baseDialog import ModelessDialog, ModalDialog

class AskDirectoryDialog(ModalDialog):
    """Ask what directory should be used for data """

    buttons = ('OK', 'Cancel')
    oneshot = True
    name    = "No data directory specified"

    #def __init__(self):
    #	"""'text' should be the question being asked"""
    #   ModalDialog.__init__(self, **kw)

    def fillInUI(self, parent):
        label_text = "Because this Demo has not been saved, and " \
                     "no data directory has been specified " \
                     "Chimera does not know where to look for data " \
                     "files when running this Demo. You can specify " \
                     "a directory to search for data files when running " \
                     "this demo, or leave blank if this Demo does not " \
                     "use any local files."
        
        import Tkinter
        t = Tkinter.Text(parent, width=50, height=5, wrap='word', relief='flat')
        t.grid(row=0, column=0, sticky="ew", columnspan=2, pady=20)
        t.insert(0.0, label_text)
        t.configure(state="disabled")

        self.temp_datadir = tkoptions.InputFileOption(parent,
                                                      1, 'Data directory', None, None,
                                                      balloon = 'Directory containing data files',
                                                      dirsOnly=True
                                                      )
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(1, weight=1)
        
    def OK(self):
        ModalDialog.Cancel(self, value=self.temp_datadir.get())
    def Cancel(self):
        ModalDialog.Cancel(self, value=None)



class AskSave(ModalDialog):
    """Ask what directory should be used for data """

    buttons  = ('Save', "Don't Save", 'Cancel')
    oneshot  = True
    title    = "Work has not been saved"

    def fillInUI(self, parent):
        label_text = "The contents of this Demo have changed since " \
                     "the last time it was saved. Do you want to  " \
                     "save your work before closing this Demo ?    "
                
        import Tkinter
        t = Tkinter.Text(parent, width=50, height=3, wrap='word', relief='flat')
        t.grid(row=0, column=0, sticky="ew", columnspan=2, pady=5)
        t.insert(0.0, label_text)
        t.configure(state="disabled")
        
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(1, weight=1)
        
    def Save(self):
        ModalDialog.Cancel(self, value='yes')
    def DontSave(self):
        ModalDialog.Cancel(self, value='no')
    def Cancel(self):
        ModalDialog.Cancel(self, value=None)


class EntryStackExec(EntryStack):

    def __init__(self, parent, editor):
        EntryStack.__init__(self, parent)

        self.editor = editor

    def doUI(self, parent):

        EntryStack.doUI(self, parent)

        self.scrFrame.grid_forget()
        self.scrFrame.grid(row=0, column=0,padx=5, columnspan=3, sticky='nsew')
        
        self.execButton = Tkinter.Button(self, command=self._execCB, text="Execute")
        self.execButton.grid(row=1,column=2, padx=20, sticky='w')

        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=10)

    def _execCB(self):
        from Midas.midas_text import makeCommand

        exec_dir = None
        
        datadir    = self.editor.gDataDirOption.get()
        if datadir:
            exec_dir = datadir
        elif self.editor.save_path:
                exec_dir = os.path.split(self.editor.save_path)[0]

        cwd = os.getcwd()
        if exec_dir:
            os.chdir(exec_dir)
        try:
            for active,cmd in self.getRows():
                if active:
                    makeCommand(cmd)
        finally:
            os.chdir(cwd)

class DemoEditor(ModelessDialog):
    
    buttons       = ('Close')
    provideStatus = True
    title         = "Demo Editor"
    oneshot       = True
    help          = "ContributedSoftware/demos/demos.html#editor"

    def __init__(self, src_path = None):
        
        self.currentPanelId = -1
        self.panels = []
        self.unique_id = 0
        
        ModelessDialog.__init__(self)

        self.NULL_PANEL = Panel(-1, self, name="")
        self.NULL_PANEL.cmdStack.delB.configure(state="disabled")
        self.NULL_PANEL.cmdStack.addB.configure(state="disabled")
        self.NULL_PANEL.undoStack.delB.configure(state="disabled")
        self.NULL_PANEL.undoStack.addB.configure(state="disabled")
        self.refreshPanelInfo(-1)
        
        self.save_path = None
        self.updateWindowTitle()

        self.gTitleOption.set("Chimera Demo")

        if src_path:
            self.loadDemo(src_path)
            self.setSavePath(src_path)
            self.updateWindowTitle() 

        self._toplevel.bind('<KeyRelease>', self.keyReleaseCB)
        self._DIRTY = False

        self._cached_save = None

    def keyReleaseCB(self, evt):
        if evt.char in string.printable + "\b":
            self.markDirty()
        
    def markDirty(self):
        self._DIRTY = True
    def markClean(self):
        self._DIRTY = False
    
    
    def _reinitialize(self):
        self.panels = []
        self.panelList.setlist([])
        self.currentPanelId = -1
        self.unique_id = 0

        self.gTitleOption.set('')
        self.gAutoDelayOption.set(5)
        self.gAutoRunOption.set(False)
        self.gImageOption.set('')
        self.gDataDirOption.set('')
        self.gBgColorOption.set(None)
        #self.textInput.clear()                                     
        self.textInput.component('text').reinitialize()
        self.setSavePath(None)
        self.updateWindowTitle()

        self.configureUpDown(-1)
        self.deleteButton.configure(state="disabled")
        
    def fillInUI(self, parent):
        self.majorPane = Pmw.PanedWidget(parent, orient='horizontal', hull_width=710, hull_height=500)
        self.majorPane.grid(row=1, column=0, sticky='nsew')

        #self.buttonFrame = Tkinter.Frame(parent)
        #self.buttonFrame.grid(row=1,column=0, sticky='ew')

        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

        self.majorPane.add('panellist')
        self.majorPane.add('panelinfo')

        #self.paneF.configurepane('demolist', size=40)
        #self.paneF.configurepane('demoinfo', size=60)
        
        self.pListFrame = self.majorPane.pane('panellist')
        self.pInfoFrame  = self.majorPane.pane('panelinfo')

        #self.demosFrame.pack(side='left', fill='both')
        #self.descFrame.pack(side='right', fill='both', expand=True)

        self.populateListFrame()
        self.populateInfoFrame()
        #self.populateButtonFrame()

        self.populateGlobalFrame()

        self.makeMenus(parent)
        from chimera.tkgui import aquaMenuBar
        aquaMenuBar(self.menuBar, parent, row = 0)
        
        self.panelList.bind('<Up>', self.doScroll)
        self.panelList.bind('<Down>', self.doScroll)


    def doScroll(self, event):
        
        listbox = self.panelList.component('listbox')

        cur_sel = listbox.curselection()
        
        if not cur_sel:
            return

        ## put this back in
        cur_index = listbox.curselection()[0]
        if not cur_index:
            return

        ## take this out
        #cur_index  = self.getCurrentPanelId()

        cur_index = int(cur_index)

        if event.keysym == 'Up':
            new_index = cur_index - 1

        elif event.keysym == 'Down':
            new_index = cur_index + 1

        if new_index < 0 or new_index >= listbox.size():
            return

        listbox.selection_clear(0, listbox.size())
        listbox.activate(new_index)
        listbox.selection_set(new_index)
        listbox.see(new_index)

        self.refreshPanelInfo(new_index)
        self.setCurrentPanelId(new_index)

    def makeMenus(self, parent):
        top = parent.winfo_toplevel()
        self.menuBar = Tkinter.Menu(top, type="menubar", tearoff=False)
        top.config(menu=self.menuBar)

        self.fileMenu = Tkinter.Menu(self.menuBar)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.fileMenu.add_command(label="Open Demo File...", command=self.Open)
        self.fileMenu.add_command(label="Run Demo", command=self.Run)
        self.fileMenu.add_command(label="Save Demo File", command = self.Save)
        self.fileMenu.add_command(label="Save Demo File As...", command=self.SaveAs)
        self.fileMenu.add_command(label="Close Demo File", command=self.Clear)
        self.fileMenu.add_command(label="Quit Editor", command=self.Close)


        self.editMenu = Tkinter.Menu(self.menuBar)
        self.menuBar.add_cascade(label="Edit", menu=self.editMenu)

        self.editMenu.add_command(label="Insert Duplicate Panel", command=self.duplicatePanel)
        
    def populateButtonFrame(self):

        self.closeButton = Tkinter.Button(self.buttonFrame, text="Close Demo",
                                          command=self.Clear)
        self.closeButton.pack(side='right', pady=5)
        
        self.saveAsButton = Tkinter.Button(self.buttonFrame, text="Save As",
                                           command=self.SaveAs)
        self.saveAsButton.pack(side='right', pady=5)

        self.saveButton = Tkinter.Button(self.buttonFrame, text="Save",
                                         command=self.Save)
        self.saveButton.pack(side='right', pady=5)

        self.openButton = Tkinter.Button(self.buttonFrame, text="Open Demo",
                                         command=self.Open)
        self.openButton.pack(side='right', pady=5)

        self.runButton = Tkinter.Button(self.buttonFrame, text="Run",
                                        command=self.Run)
        self.runButton.pack(side='right', pady=5)

        help.register(self.openButton,   balloon="Open a Demo file in editor")
        help.register(self.saveButton,   balloon="Save Demo to file")
        help.register(self.saveAsButton, balloon="Save Demo to new file")
        help.register(self.closeButton,  balloon="Close current Demo")
        help.register(self.runButton,    balloon="Run a Demo from current panels in editor")

    def populateListFrame(self):
        
        self.panelsLabel = Tkinter.Label(self.pListFrame, text="Panels", font="helvetica -14 bold")
        self.panelsLabel.grid(row=0, column=0, columnspan=4, sticky='w')
        
        self.panelList = Pmw.ScrolledListBox(self.pListFrame,
                                             labelmargin=10,
                                             listbox_height=5, listbox_width=20,
					     listbox_selectmode=Tkinter.SINGLE,
					     selectioncommand=self.refreshPanelCB,
                                             listbox_exportselection=False)
                                             #dblclickcommand=self.showPanelEntry)
        self.panelList.grid(row=1, column=0, padx=10, columnspan=4, sticky='nsew')

        
        this_dir = os.path.split(Demo.__file__)[0]
	self.upButton = Tkinter.Button(self.pListFrame, command=self.panelUp)
        up_image=chimage.get("arrow_up.gif", self.upButton)#text="/\\")
        self.upButton.configure(image=up_image, state="disabled")
        self.upButton._image = up_image
        help.register(self.upButton, balloon="Move currently selected panel up")
	self.upButton.grid(row=2,column=0,sticky='s')

	self.downButton=Tkinter.Button(self.pListFrame, command=self.panelDown)
        down_image=chimage.get("arrow_down.gif", self.downButton)#text="/\\")
        self.downButton.configure(image=down_image, state="disabled")
        self.downButton._image = down_image
        help.register(self.downButton, balloon="Move currently selected panel down")
	self.downButton.grid(row=3,column=0,sticky='n')

	self.deleteButton = Tkinter.Button(self.pListFrame, text="Delete", command=self.deletePanel, state="disabled")
        help.register(self.deleteButton, balloon="Delete currently selected panel")
        self.deleteButton.grid(row=2,column=1,rowspan=2)

        self.newButton = Tkinter.Button(self.pListFrame, text="New", command=self.newPanelCB)
        help.register(self.newButton, balloon="Add a new panel")
        self.newButton.grid(row=2, column=2,rowspan=2)

        #self.editGlobalB = Tkinter.Button(self.pListFrame, text="Edit Demo Options",
        #                                  command=self.editGlobalCB)
        #help.register(self.editGlobalB, balloon="Edit global options for Demo")
        #self.editGlobalB.grid(row=4,column=0,columnspan=4, sticky='w')
	
        self.pListFrame.rowconfigure(0, weight=1)
        self.pListFrame.rowconfigure(1, weight=20)
        self.pListFrame.rowconfigure(2, weight=1)
	self.pListFrame.rowconfigure(3, weight=1)
        self.pListFrame.rowconfigure(4, weight=1)

        #self.pListFrame.columnconfigure(1,weight=1)
        
    def populateInfoFrame(self):
        
        self.panelNB = Pmw.NoteBook(self.pInfoFrame)
        self.panelNB.grid(row=0,column=0,sticky='nsew')
        self.pInfoFrame.rowconfigure(0,weight=1)
        self.pInfoFrame.columnconfigure(0,weight=1)

        self.panelNB.add('content', tab_text='Panel Content')
        self.panelNB.add('options', tab_text='Panel Options')
        self.panelNB.add('global',  tab_text='Demo Options')
        self.pContentFrame = self.panelNB.page('content')
        self.pOptionsFrame = self.panelNB.page('options')
        self.gOptionsFrame = self.panelNB.page('global')

        self.pOptionsLabel = Tkinter.Label(self.pOptionsFrame, text="")                                           
        self.pOptionsLabel.grid(row=0,column=0,sticky='ew', pady=20)

        self.pDelayOption = tkoptions.StringOption(self.pOptionsFrame,
                                                   1, 'Panel delay', '', None,
                                                   balloon = "Time to wait before advancing to next " \
                                                   "panel (overrides default delay)",
                                                   borderwidth=1
                                                   )

        #self.delayEntry = Pmw.EntryField(self.pOptionsFrame, labelpos='w',
        #                                     labelmargin=5,
        #                                     label_text = "Delay",
        #                                     validate='numeric')
        #                                     
        #self.delayEntry.grid(row=0,column=0,sticky='w')

        self.pOptionsFrame.rowconfigure(2,weight=1)
        
        self.pOptionsFrame.columnconfigure(0,weight=1)
        self.pOptionsFrame.columnconfigure(1,weight=8)
        self.pOptionsFrame.columnconfigure(2,weight=2)

        self.panelNameFrame = Tkinter.Frame(self.pContentFrame,
                                            relief=Tkinter.RIDGE)
        self.panelNameFrame.grid(row=0,sticky='ew',padx=10,pady=5)

        self.panelNameTitle = Tkinter.Label(self.panelNameFrame,
                                            text="Panel title:  ",
                                            )
        
        self.panelNameEntry = Tkinter.Entry(self.panelNameFrame,
                                            font="helvetica -14 bold",
                                            relief=Tkinter.SUNKEN,
                                            #bd=2,
                                            width=30)
        
        self.panelNameEntry.bind("<Return>", self.processPanelName)
        self.panelNameEntry.grid(row=0,column=1,sticky='w')
        
        #self.panelNameLabel = Tkinter.Label(self.panelNameFrame,
        #                                    font="helvetica -14 bold",
        #                                    relief=Tkinter.FLAT
        #                                    #bd=2,)
        #                                    )
                                            
        #self.panelNameLabel.grid(row=0,column=1,sticky='w')
        #self.panelNameLabel.bind("<Double-Button-1>", self.showPanelEntry)
        #help.register(self.panelNameLabel, balloon="Double-click to change panel title")

        self.minorPane = Pmw.PanedWidget(self.pContentFrame, orient='vertical')
        self.minorPane.grid(row=1, column=0, columnspan=2, sticky='nsew')

        self.panelNameFrame.columnconfigure(0,weight=1)
        self.panelNameFrame.columnconfigure(1, weight=50)
        
        self.pContentFrame.rowconfigure(0, weight=1)
        self.pContentFrame.rowconfigure(1, weight=20)
        self.pContentFrame.columnconfigure(0, weight=1)

        self.minorPane.add('textframe',size=.5)
        self.minorPane.add('cmdsframe',size=.5)
        self.textFrame = self.minorPane.pane('textframe')
        self.cmdsFrame = self.minorPane.pane('cmdsframe')

        self.populateTextFrame()
	self.populateCmdsFrame()

    def populateTextFrame(self):

        self.textLabel = Tkinter.Label(self.textFrame, text="Text", font="helvetica -14 bold")
        self.textLabel.grid(row=0, sticky='w', pady=5)

        self.textInput = Pmw.ScrolledText(self.textFrame,
					  text_pyclass = HtmlText,
					  text_relief = 'sunken',
					  text_wrap = 'word',
					  #text_height=10,
					  #text_width=50
					  )
	self.textInput.grid(row=1,sticky='nsew',padx=5)
        
	self.previewCheckB = Tkinter.Checkbutton(self.textFrame, text="Preview",
                                                 command = self.previewCB)
	self.previewCheckB.grid(row=2, sticky='e',pady=10)
        help.register(self.previewCheckB, balloon="Preview text as rendered HTML")
	
	self.textFrame.rowconfigure(0,weight=1)
	self.textFrame.rowconfigure(1, weight=30)
	self.textFrame.rowconfigure(2, weight=1)

	self.textFrame.columnconfigure(0,weight=1)

    def populateGlobalFrame(self):
        #self.gOptionsFrame = Tkinter.Frame(self.pInfoFrame)
        ## autodelay, autorun, image, bgcolor
        self.globalOptionsLabel = Tkinter.Label(self.gOptionsFrame,
                                                text="")
        self.globalOptionsLabel.grid(row=0,column=0,sticky='w',padx=5,pady=20)
        
        self.gTitleOption  = tkoptions.StringOption(self.gOptionsFrame,
                                                    1, 'Demo title', '', self.updateWindowTitle,
                                                    balloon = "Demo title",
                                                    borderwidth=1
                                                    )
        self.gDataDirOption = tkoptions.InputFileOption(self.gOptionsFrame,
                                                        2, 'Data directory', None, None,
                                                        balloon = 'Directory containing data files',
                                                        dirsOnly=True
                                                        )
        
        self.gAutoDelayOption = tkoptions.StringOption(self.gOptionsFrame,
                                                       3, 'Default delay', '5', None,
                                                       balloon = "Time to wait before advancing to next panel",
                                                       borderwidth=1
                                                    )
        self.gAutoRunOption = tkoptions.BooleanOption(self.gOptionsFrame,
                                                      4, 'AutoRun on start', False, None,
                                                      balloon = "Demo starts in AutoRun mode"
                                                      )
        self.gImageOption = tkoptions.InputFileOption(self.gOptionsFrame,
                                                      5, 'Image', None, None,
                                                      balloon = 'Image to appear in Demo window' 
                                                      )
        self.gBgColorOption = tkoptions.ColorOption(self.gOptionsFrame,
                                                    6, 'Image background color', None, None,
                                                    balloon = "Color to appear behind image"
                                                    )
        
        self.gOptionsFrame.rowconfigure(7,weight=1)
        
        self.gOptionsFrame.columnconfigure(0, weight=1)
        self.gOptionsFrame.columnconfigure(1, weight=8)
        self.gOptionsFrame.columnconfigure(2, weight=2)
        
        #self.gAutoDelayOption.grid(row=0,column=0, sticky='ew')
                                                    
    def previewCB(self):
        if self.getCurrentPanelId() == -1: return

	if self.getCurrentPanel().getPreviewVar().get():
	    self.cur_text_content = self.textInput.get(0.0, Tkinter.END)
            #print "CURRENT CONTENT IS\n********"
            #print self.cur_text_content
            #print "************\n"
	    self.textInput.delete(0.0, Tkinter.END)
            #try:
            self.textInput.component('text').reinitialize()

            self.refreshTextBox(self.cur_text_content, mode='preview')
            #except Tkinter.TclError, what:
            #    print "CURRENT CONTENT IS ", self.cur_text_content
            #    self.textInput.delete(0.0, Tkinter.END)
            #    Tkinter.Text.insert(self.textInput.component('text'), 0.0, self.cur_text_content.rstrip())
            #    raise UserError("Error occurred while rendering html: %s" % what) 
            #else:
            self.makeTextPreview()
	else:
            self.makeTextNormal()
	    self.textInput.delete(0.0, Tkinter.END)
            self.refreshTextBox(self.cur_text_content.rstrip())
            
	    
    def makeTextNormal(self):
        self.textInput.configure(text_relief='sunken', text_state='normal')
        
    def makeTextPreview(self):
        self.textInput.configure(text_relief='sunken', text_state='disabled')

    def populateCmdsFrame(self):

        ## commands
        self.cmdsLabel = Tkinter.Label(self.cmdsFrame, text="Panel commands", font="helvetica -14 bold")
	self.cmdsLabel.grid(row=0,column=0, sticky='w',pady=5)

        this_dir = os.path.split(Demo.__file__)[0]
	
        ## undos
	self.undoLabel = Tkinter.Label(self.cmdsFrame, text="Undo commands", font="helvetica -14 bold")
	self.undoLabel.grid(row=0, column=1, sticky='w', pady=5)

	self.cmdsFrame.rowconfigure(0,weight=0)
	self.cmdsFrame.rowconfigure(1, weight=10)
        self.cmdsFrame.columnconfigure(0,weight=1)
        self.cmdsFrame.columnconfigure(1,weight=1)
        

    #def showPanelEntry(self,event=None):
    #    self.panelNameLabel.grid_forget()
    #    self.panelNameEntry.grid(row=0,column=1,sticky='w')
    #    #self.panelNameEntry.delete(0,Tkinter.END)
    #    #self.panelNameEntry.insert(0,self.getCurrentPanel().getNameVar().get())
        
    #def showPanelLabel(self, event=None):
    #    new_label = self.panelNameEntry.get()
    #    cur_panel = self.getCurrentPanel()
    #    #cur_panel.setName(new_label)
    #    #cur_sel = int(self.panelList.index(Tkinter.ACTIVE))
    #    if new_label.strip() == '':
    #        new_label = cur_panel.getOrigName()
    #        cur_panel.setName(new_label)
    #    self.updatePanelName(self.getCurrentPanelId(), new_label)
    #    
    #    #self.panelNameVar.set(new_label)
    #    self.panelNameEntry.grid_forget()
    #    self.panelNameLabel.grid(row=0, column=1, sticky='w')

    #def editGlobalCB(self):
    #    self.panelNB.grid_forget()
    #    self.gOptionsFrame.grid(row=0,column=0,sticky='nsew')


    def deletePanel(self):

        to_delete = self.getCurrentPanelId()
        if to_delete == -1:
            ## can't delete the NULL panel
            return
	
        if self.panelCount() == 1:
            self.refreshPanelInfo(-1)
            self.setCurrentPanelId(-1)
            self.deleteButton.configure(state="disabled")
            
        elif to_delete < self.panelCount() - 1:
            ## activate the next one in the list
            self.activateListItem(to_delete+1)
            self.refreshPanelInfo(to_delete+1)
            self.setCurrentPanelId(to_delete)
        else:
            ## activate the previous one in the list
            self.activateListItem(to_delete-1)
            self.refreshPanelInfo(to_delete-1)
            self.setCurrentPanelId(to_delete-1)

        self.panelList.delete( to_delete )
	del self.panels[ to_delete ]


        self.configureUpDown(to_delete)
        #if self.panelCount() == 1:
        #    self.configureUpDown(0)
        #elif self.panelCount() == 0:
        #    self.configureUpDown(-1)
        
        self.markDirty()

    def newPanelCB(self):
        cur_sel = self.getCurrentPanelId()
        insert_target = cur_sel + 1
        
        new_panel = self.makeNewPanel(insert_idx=insert_target)

        self.activateListItem(insert_target)
	self.refreshPanelInfo(insert_target)
        self.setCurrentPanelId(insert_target)

        self.deleteButton.configure(state="normal")
        self.markDirty()

    def makeNewPanel(self, insert_idx=None, name=None):
        new_id = self.getNewPanelId()
	new_panel = Panel(new_id, self, name=name)

        if insert_idx:
            self.panels.insert(insert_idx, new_panel)
            self.panelList.insert(insert_idx, new_panel.getName())
        else:
            self.panels.append(new_panel)
            self.panelList.insert(Tkinter.END, new_panel.getName())

        return new_panel
        

    def activateListItem(self, id):
        self.panelList.component('listbox').select_clear('active')
        self.panelList.component('listbox').select_set(id)
	self.panelList.component('listbox').activate(id)

    def panelUp(self):

        cur_sel = self.getCurrentPanelId()
        if cur_sel <= 0: return

        prev_idx = cur_sel-1
        
        #print "cur_sel is %s" % cur_sel
        #print "prev_idx is %s" % prev_idx
        
        new_panel_list = [p.getName() for p in self.panels]
        #new_panel_list[0:prev_idx] = [p.getName() for p in self.panels[0:prev_idx]]
        new_panel_list[prev_idx] = self.getPanel(cur_sel).getName()
        new_panel_list[cur_sel]  = self.getPanel(prev_idx).getName()
        #new_panel_list[cur_sel+1:] = [p.getName() for p in self.panels[cur_sel+1:]]
        self.panelList.setlist(new_panel_list)
        del new_panel_list

        self.activateListItem(prev_idx)
        self.setCurrentPanelId(prev_idx)
        self.configureUpDown(prev_idx)
        
        tmp_panel = self.getPanel(cur_sel)
        self.panels[cur_sel] = self.panels[cur_sel-1]
        self.panels[cur_sel-1] = tmp_panel
        self.markDirty()
	
    def panelDown(self):
        
        cur_sel = self.getCurrentPanelId()
        if (cur_sel == -1) or (cur_sel == self.panelCount()-1):
            return

        next_idx = cur_sel + 1

        new_panel_list = [p.getName() for p in self.panels]
        new_panel_list[next_idx] = self.getPanel(cur_sel).getName()
        new_panel_list[cur_sel]  = self.getPanel(next_idx).getName()
        self.panelList.setlist(new_panel_list)
        del new_panel_list

        self.activateListItem(next_idx)
        self.setCurrentPanelId(next_idx)
        self.configureUpDown(next_idx)
        
        tmp_panel = self.getPanel(cur_sel)
        self.panels[cur_sel] = self.panels[cur_sel+1]
        self.panels[cur_sel+1] = tmp_panel
        self.markDirty()
        
    def panelCount(self):
	return len(self.panels)
            
    def getNewPanelId(self):
        new_id = self.unique_id
        self.unique_id += 1
        return new_id
        
    def getCurrentPanel(self):
        if self.getCurrentPanelId() == -1:
            return self.NULL_PANEL
        else:
            return self.panels[self.getCurrentPanelId()]
    
    def getCurrentPanelId(self):
	return self.currentPanelId
    def setCurrentPanelId(self, id):
	self.currentPanelId = int(id)

    def getPanel(self,id):
        if id==-1:
            return self.NULL_PANEL
        else:
            return self.panels[id]

    def refreshPanelCB(self):
        cur_sel = self.panelList.curselection()
        if not cur_sel:
            return
        cur_idx = int(cur_sel[0])
        self.refreshPanelInfo(cur_idx)
        self.setCurrentPanelId(cur_idx)
        self.panelList.focus_set()
    
    def refreshPanelInfo(self, refresh_idx):
        ## if you're gonna refresh to your current panel, don't
        ## do anything
        #if self.getCurrentPanelId() == refresh_idx:
        #    print "RETURNING AT TOP!"
        #    return

        ## don't need this if global is in a tab
        #self.gOptionsFrame.grid_forget()
        #self.panelNB.grid(row=0,column=0,sticky='nsew')
        
        ##out with the old.....
        old_panel = self.getCurrentPanel()

        old_panel.forgetCmdStack()
        old_panel.forgetUndoStack()

        if old_panel.getPreviewVar().get():
            old_panel.setText(self.cur_text_content)
        else:
            old_panel.setText(self.textInput.get(0.0, Tkinter.END).rstrip())
        self.makeTextNormal()
        self.textInput.delete(0.0, Tkinter.END)

        if self.getCurrentPanelId() != -1:
            self.processPanelName()

        if refresh_idx != -1:
            self.configurePanelInput(1)
        
        ## in with the new....
        new_panel = self.getPanel(refresh_idx)

        self.pDelayOption._option.configure(textvariable=new_panel.getDelayVar())
        #self.pDelayOption.set(new_panel.getDelay())

        new_panel.showCmdStack()
        new_panel.showUndoStack()

        self.panelNameEntry.configure(textvariable=new_panel.getNameVar())
        #self.panelNameLabel.configure(textvariable=new_panel.getNameVar())
        self.panelNameTitle.grid(row=0,column=0, pady=5, sticky='nsew')

        new_preview_var = new_panel.getPreviewVar()
        self.previewCheckB.configure(variable=new_preview_var)

        raw_text = new_panel.getText()
        #print "GOT BACK!! ", raw_text
        if new_preview_var.get():
            self.refreshTextBox(raw_text, mode='preview')
            self.makeTextPreview()
        else:
            self.refreshTextBox(raw_text)
        self.cur_text_content = raw_text

        if refresh_idx == -1:
            self.panelNameTitle.grid_forget()
            self.panelNameEntry.grid_forget()
            self.configurePanelInput(0)
        else:
            self.panelNameTitle.grid(row=0,column=0)
            self.panelNameEntry.grid(row=0,column=1, sticky='w')

        self.configureUpDown(refresh_idx)


    def configureUpDown(self, idx):

        if idx < self.panelCount()-1:
            self.downButton.configure(state="normal")
        else:
            self.downButton.configure(state="disabled")

        if idx > 0 and self.panelCount()>1:
            self.upButton.configure(state="normal")
        else:
            self.upButton.configure(state="disabled")

    
    def refreshTextBox(self, text, mode='normal'):
        if mode == 'normal':
            Tkinter.Text.insert(self.textInput.component('text'),0.0, text)
        elif mode == 'preview':
            try:
                self.textInput.insert(0.0, text)
            except HtmlParseError, what:
                self.status("Error parsing HTML: %s" % what, \
                            blankAfter=10, color='red')
     
    def configurePanelInput(self, mode):
        for widg in (self.textInput.component('text'),
                     self.previewCheckB, self.pDelayOption._option):
            widg.configure(state=['disabled','normal'][mode])

    def processPanelName(self, event=None):
        new_label = self.panelNameEntry.get()
        cur_panel = self.getCurrentPanel()
        #print "new_label is ", new_label

        if new_label.strip() == '':
            orig_name = cur_panel.getOrigName()
            cur_panel.getNameVar().set(orig_name)
            self.updatePanelName(self.getCurrentPanelId(), orig_name)
        else:
            cur_panel.setName(new_label)
            self.updatePanelName(self.getCurrentPanelId(), new_label)
    
    def updatePanelName(self, id, name):
        panel_names = [p.getName() for p in self.panels]
        panel_names[id] = name
        self.updatePanelList()
        
    def updatePanelList(self):
        cur_sel = self.panelList.index('active')
        self.panelList.setlist([p.getName() for p in self.panels])
        self.activateListItem(cur_sel)


    ## Button callbacks

    def duplicatePanel(self):
        self.refreshPanelInfo(self.getCurrentPanelId())
        p = self.getCurrentPanel()
        
        if p.id < 0: return

        panel_text = p.getText()
        panel_name = p.getName() + " copy"

        panel_cmds =  p.getCmds()
        panel_undos = p.getUndos()

        panel_delay = p.getDelayVar().get()

        cur_item = self.panelList.index('active')
        if cur_item == None:
            ## get the count before adding the new panel
            ## (to acct. for the 0-index) - this will tell
            ## you the next index
            insert_target = self.panelCount()
        else:
            insert_target = cur_item + 1
        new_panel = self.makeNewPanel(insert_idx=insert_target, name=panel_name)

        new_panel.getDelayVar().set(panel_delay)
        new_panel.setText(panel_text)
        
        for c in panel_cmds:
            active, content = c
            new_panel.addCmd(active,content)

        for u in panel_undos:
            active, content = u
            new_panel.addUndo(active,content)

        self.activateListItem(insert_target)
	self.refreshPanelInfo(insert_target)
        self.setCurrentPanelId(insert_target)

        self.markDirty()

    def Run(self):

        from OpenSave import osTemporaryFile
        tmp_path = osTemporaryFile()
        self.writeDemo(tmp_path, tempMode=True)

        if not self.save_path and not self.gDataDirOption.get():
            self.status("No data location specified! Demo may not be able to find local data files.", color='red',
                        blankAfter=20)
        
        Demo.openDemo(tmp_path)

    def Save(self):
        if self.save_path:
            self.writeDemo(self.save_path)
            self.status("Demo has been saved", color="blue", blankAfter=10)
        else:
            self.SaveAs()

        self.markClean()

    def SaveAs(self):
        from OpenSave import SaveModeless
        SaveModeless(command=self._writeCB, title="Choose Demo Save Location",
                     dialogKw={'oneshot':1}, historyID="Demo editor save as",
                     defaultFilter=0, filters=[("Demo", ["*.src"], ".src")]
                     )
        
        self.markClean()
        
    def Open(self):
        close_it = self.checkIfDirty()
        if not close_it: return
            
        from OpenSave import OpenModeless
        OpenModeless(command=self._openCB, title="Choose Demo to Open",
                     dialogKw={'oneshot':1}, historyID="Demo editor open",
                     defaultFilter=0, filters=[("Demo", ["*.src"])]
                     )

    def Clear(self):

        close_it = self.checkIfDirty()

        if close_it:
            self.markClean()
            self.refreshPanelInfo(-1)
            self._reinitialize()
        
    def Close(self):

        from OpenSave import osTemporaryFile
        self._cached_save = osTemporaryFile()
        self.writeDemo(self._cached_save)
        
        close_it = self.checkIfDirty()

        if close_it:
            ModelessDialog.Close(self)
        else:
            self._cached_save = None

    def checkIfDirty(self):
        if self._DIRTY:
            import chimera
            ask_save= AskSave()
            res = ask_save.run(chimera.tkgui.app)

            if res == 'yes':
                self.Save()
                return True
            elif res == 'no':
                return True
            else:
                return False
        else:
            return True

    def setSavePath(self, path):
        self.save_path = path

    def _writeCB(self, okayed, dialog):
        if okayed:
            path = dialog.getPaths()[0]
            
            if self._cached_save:
                ## means the editor dialog is about to close
                import shutil
                shutil.copyfile(self._cached_save, path)
                self._cached_save = None
            else:
                self.writeDemo(path)
                self.status("Demo has been saved", color="blue", blankAfter=10)
                self.setSavePath(path)
                self.updateWindowTitle()

    def _openCB(self, okayed, dialog):
        if okayed:
            for path in dialog.getPaths():
                self.loadDemo(path)
                self.setSavePath(path)
                self.updateWindowTitle()

    def loadDemo(self, src_path):
        ## clear out current contents
        self.refreshPanelInfo(-1)
        self._reinitialize()
        
        from multiloader2 import Multiloader
        m = Multiloader()
        m.load( src_path, [XMLDemo] )
        objs = m.getObjects()
        #print objs
        demoObjs  = objs['Demo']
        #panelObjs = objs['Panel'] 
        demoObj = demoObjs[0]

        ## re-constitute global options
        if hasattr(demoObj, 'title'):
            self.gTitleOption.set(str(demoObj.title) )
        if hasattr(demoObj, 'autodelay'):
            self.gAutoDelayOption.set( int(demoObj.autodelay) )
        if hasattr(demoObj, 'image'):
            self.gImageOption.set( str(demoObj.image) )
        if hasattr(demoObj, 'datadir'):
            self.gDataDirOption.set( str(demoObj.datadir) )
        #if hasattr(demoObj, 'bg_color'):
        #    self.gBgColorOption.set( )
        if hasattr(demoObj, 'autorun_on'):
            self.gAutoRunOption.set(1)
        #if hasattr(demoObj, 'description'):
        #    self.descrip

        ## can be three things - None, a single item, or a list
        if not demoObj.panels: demoObj.panels = []
        elif isinstance(demoObj.panels, XMLPanel):
            demoObj.panels = [demoObj.panels]
            
        for p in demoObj.panels:

            demo_panel = self.makeNewPanel()

            ## re-constitute panel options
            if hasattr(p, 'autodelay'):
                demo_panel.delay_var.set(str(p.autodelay))
            if hasattr(p, 'title'):
                demo_panel.name_var.set(str(p.title))
                
            ##re-constitute text state
            panel_text = ''
            if p.text:
                panel_text = str(p.text)
            
            if panel_text.strip():
                demo_panel.setText(panel_text.strip())
                
            ## re-constitute command state
            cmds = []
            if p.command:
                if isinstance(p.command, XMLCommand):
                    if not hasattr(p.command, 'active'): p.command.active="False" ## stopgap
                    cmds = [ ([False,True][p.command.active=="True"], str(p.command.item).strip()) ]
                elif isinstance(p.command, list):
                    for c in p.command:
                        if not hasattr(c,'active'): c.active="True"
                        cmds.append( ([False,True][c.active=="True"],str(c.item).strip()) )

            for c in cmds:
                demo_panel.addCmd(c[0], c[1])
                
            ## re-constitute undo state
            undos = []
            if p.undo:
                if isinstance(p.undo, XMLUndo):
                    if not hasattr(p.undo, 'active'): p.undo.active="False" ## stopgap
                    undos = [ ([False,True][p.undo.active=="True"], str(p.undo.item).strip()) ]
                if isinstance(p.undo, list):
                    for u in p.undo:
                        if not hasattr(u, 'active'): u.active="False"
                        undos.append( ([False,True][u.active=="True"],str(u.item).strip()) )
                    

            for u in undos:
                demo_panel.addUndo(u[0], u[1])

        self.markClean()
        if self.panelCount() > 0:
            self.deleteButton.configure(state="normal")
            
            self.activateListItem(0)
            self.refreshPanelInfo(0)
            self.setCurrentPanelId(0)

            self.updatePanelList()


    #def setWindowTitle(self):
    #    pass
    #def setWindowPath(self):
    #    pass

    def updateWindowTitle(self, data=None):
        title_str = "%s - " % self.title
        title_str += "%s " % (self.gTitleOption.get() or "(Untitled Demo)")
        if self.save_path:
            trunc_path = self.getTruncPath(self.save_path)
            title_str += "[ %s ]" % trunc_path
            
        self._toplevel.title(title_str)


    def getTruncPath(self, path):
        path_elts = path.split(os.path.sep)

        ## becuase save path is absolute, the first elt will be ''
        if not path_elts[0]:
            path_elts = path_elts[1:]

        if len(path_elts) <= 6:
            return path
        else:
            first_three = os.path.join(*path_elts[0:3])
            #print "first_three is ", first_three 
            last_three  = os.path.join(*path_elts[-3:])
            #print "last_three is ", last_three 

            return os.path.join('', first_three, " ... ", last_three)

        ## don't need the last 
        #path_elts = path_elts[:-1]
        

    def writeDemo(self, save_path, tempMode=False):
        from CGLtk.color import rgba2tk
        from multiloader2 import Multiloader
        m = Multiloader()

        ## GLOBAL options
        demo = XMLDemo()
        title       = self.gTitleOption.get()
        if title:
            demo.title = title
        else:
            demo.title = "Chimera Demo"
        
        autodelay   = self.gAutoDelayOption.get()
        if autodelay:
            demo.autodelay = autodelay
            
        image       = self.gImageOption.get()
        if image:
            demo.image = image

        datadir    = self.gDataDirOption.get()
        if datadir:
            demo.datadir = datadir
        else:
            if tempMode and self.save_path:
                demo.datadir = os.path.split(self.save_path)[0]
            
        bg_color    = self.gBgColorOption.get()
        if bg_color:
            demo.bg_color = rgba2tk(bg_color.rgba())
            
        autorun_on  = self.gAutoRunOption.get()
        if autorun_on:
            demo.autorun_on = autorun_on
            
        demo.description = ''

        panel_list = []

        panel_id = 0
        ##PANEL information
        for p in self.panels:

            panel_id += 1
            panel = XMLPanel()

            panel.id = panel_id
            delay = p.getDelayVar().get()
            if delay:
                panel.autodelay = delay

            title = p.getNameVar().get()
            if title:
                if not title[0:9] == "<untitled":
                    panel.title = title
                           
            if p == self.getCurrentPanel():
                panel.text = self.getCurrentText()
            else:
                panel.text = p.getText().strip()

            
            panel.command = []
            for var,entry in p.getCmds():
                xmlc = XMLCommand()
                xmlc.active = ["False","True"][var]
                xmlc.item   = entry
                panel.command.append(xmlc)                        
                
            
            panel.undo = []
            for var,entry in p.getUndos():
                xmlu = XMLUndo()
                xmlu.active = ["False","True"][var]
                xmlu.item   = entry
                panel.undo.append(xmlu)

            panel_list.append(panel)

        demo.panels = panel_list

        m.save(save_path, {'Demo':[demo]})
        
                        
        
##     def saveDemo2(self, path):
##         from CGLtk.color import rgba2tk
        
##         try:
##             f = open(path, 'w')
##         except IOError, what:
##             raise UserError, what

##         f.write("[INFO]\n")

##         title = self.gTitleOption.get().strip()
##         if title:
##             f.write("TITLE %s\n" % title)

##         auto_delay = self.gAutoDelayOption.get()
##         if auto_delay:
##             f.write("AUTODELAY %d\n" % int(auto_delay))

##         autorun_on = self.gAutoRunOption.get()
##         if autorun_on:
##             f.write("AUTORUN_ON\n")

##         image_dir = self.gImageOption.get()
##         if image_dir:
##             f.write("IMAGE %s\n" % os.path.split(image_dir)[1])

##         color = self.gBgColorOption.get()
##         if color:
##             f.write("BG_COLOR %s\n" % rgba2tk(color.rgba()))

##         f.write("[END INFO]\n\n")
        
##         for p in self.panels:

##             per_panel_data = ""
##             if p.getDelayVar().get():
##                 per_panel_data += " AUTODELAY=%d" % int(p.getDelayVar().get())
##             if p.getNameVar().get() and (p.getNameVar().get()[0:5]!='Panel'):
##                 per_panel_data += " TITLE=%s" % p.getNameVar().get().replace(" ","_")

                
##             f.write("[START%s]\n" % per_panel_data)
##             if p.getTextVar().get():
##                 f.write("[TEXT]\n")
##                 if p == self.getCurrentPanel():
##                     self.writeOutCurrentText(f)
##                 else:
##                     f.write("%s\n" % p.getText().strip())
##                 f.write("[END TEXT]\n")

##             if p.getCommandVar().get():
##                 f.write("[COMMANDS]\n")
##                 for check,var,entry in p.getCmds():
##                     if var.get():
##                         f.write("%s\n" % entry.get())
##                 f.write("[END COMMANDS]\n")
                
##             if p.getUndoVar().get():
##                 f.write("[UNDO]\n")
##                 for check,var,entry in p.getUndoWidgets():
##                     if var.get():
##                         f.write("%s\n" % entry.get())
##                 f.write("[END UNDO]\n")
                

##             f.write("[END]\n\n")

##         f.close()

##         #import chimera
##         #chimera.openModels.open(TEST_SRC)

    def writeOutCurrentText(self, f):
        p = self.getCurrentPanel()
        if p.getPreviewVar().get():
            f.write("%s\n" % self.cur_text_content.strip())
        else:
            f.write("%s\n" % self.textInput.get().strip())

    def getCurrentText(self):
        p = self.getCurrentPanel()
        if p.getPreviewVar().get():
            return self.cur_text_content.strip()
        else:
            return self.textInput.get().strip()

#import chimera
#dialogs.register(DemoEditor.name, DemoEditor)


class Panel:
    def __init__(self, id, ed, name=None):
	self.id = id

        self.name_var = Tkinter.StringVar()

        self.editor = ed
        
        if name != None:
            self.name_var.set(name)
            self.orig_name = name
        else:
            self.name_var.set("<untitled %s>" % (id+1))
            self.orig_name =  "<untitled %s>" % (id+1)

        self.preview_var   = Tkinter.IntVar()

        self.delay_var     = Tkinter.StringVar()
        self.delay_var.set('')
        #self.delay = ''

        self.text          = ''

        self.cmdStack  = EntryStackExec(self.editor.cmdsFrame, self.editor)
        self.undoStack = EntryStackExec(self.editor.cmdsFrame, self.editor)
    

    def forgetUndoStack(self):
        self.undoStack.grid_forget()
    def forgetCmdStack(self):
        self.cmdStack.grid_forget()

    def showCmdStack(self):
        self.cmdStack.grid(row=1,column=0, sticky='nsew')
    def showUndoStack(self):
        self.undoStack.grid(row=1,column=1, sticky='nsew')


    def addCmd(self, active, cmd):
        self.cmdStack.addRow(active,cmd)
    def addUndo(self, active, undo):
        self.undoStack.addRow(active, undo)
        
    def getUndos(self):
	return self.undoStack.getRows()
    def getCmds(self):
	return self.cmdStack.getRows()


    def getUndoVar(self):
        return self.undo_var
    def setUndoVarVal(self, val):
        self.undo_var.set(val)
    def getPreviewVar(self):
        return self.preview_var

    def getDelayVar(self):
        return self.delay_var
    
    def setName(self, name):
        #print "setting name to ", name
        self.name_var.set(name)
    def getNameVar(self):
        return self.name_var
    def getName(self):
        return self.name_var.get()

    def getOrigName(self):
        return self.orig_name
    
    def setText(self, text):
        self.text = text
    def getText(self):
        return self.text
        
    
## ISSUES
## need to scroll undo and cmd frames to 'see' last widget (hard)
## whats up with typing when -1 is displayed (OK)
## imgs on buttons
## make panellist scrollable
