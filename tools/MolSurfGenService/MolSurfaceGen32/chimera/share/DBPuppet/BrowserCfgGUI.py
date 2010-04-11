# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: BrowserCfgGUI.py 26655 2009-01-07 22:02:30Z gregc $

from chimera.WizShell import WizShell
import FileTypeMan
from chimera import pathFinder
from chimera import fileInfo
import os.path
import FileTypeMan
import Tkinter, Pmw, Tix


FileTypeDescs = {
    "Chimera web data": "Instructs Chimera to open " \
    "models and/or execute arbitrary commands",
    "Python": "Python programming language code",
    "Mol2": "Molecular structure in Mol2 file format",
    "VRML": "Graphical objects in Virtual Reality " \
    "Modeling Language file format",
    "PDB": "Molecular structure in Protein Data Bank file format"
    }


class BrowserCfgGUI(WizShell):

    name    = "Browser Configuration"
    buttons = ("Back", "Next", "Close")
    help    = "ContributedSoftware/webdata/webdata.html"
    
    def __init__(self):

        pf = pathFinder()
        img_src = os.path.join(pf.dataRoot, "DBPuppet", "image_bs.gif")

        WizShell.__init__(self, 4, 450, 175, img_src, img_bg_color='black')

        self.ftm = FileTypeMan.FileTypeMan()

        self.configStatus = True
        self.configStatusString = ''

        self.createPanelOne()
        self.createPanelTwo()
        self.createPanelThree()
        self.createPanelFour()


    def createPanelOne(self):
        self.createTitle(0, "Browser Configuration")
        self.createExplanation(0, "This utility will guide you through the process of configuring " \
                    "your system to open certain types of files using Chimera." \
                    "\n" \
                    "Click next to continue..."
                    )

    def createPanelTwo(self):
        self.createTitle(1, "File Types")
        self.createExplanation(1, "Chimera currently supports the following file types.\n" \
                               "Click on the appropriate boxes to enable Chimera to open " \
                               "the corresponding file types from a web browser.")



        self.desc_txt = Tkinter.Text(self.pInterior(1), relief = 'flat',
                                     wrap = 'word',
                                     pady=15,
                                     height=1,
                                     width=50)
        self.desc_txt.pack(side='bottom', anchor='w', fill='x', padx=10)
        self.desc_txt.insert(0.0, "No type selected")
        self.desc_txt.configure(state="disabled", background=self.pInterior(1).cget('background'))
        

        desc_lbl = Tkinter.Label(self.pInterior(1), text="Description:",
                                      font=("arial", 10, 'bold'), relief = "flat")
        desc_lbl.pack(side='bottom', anchor = 'w', padx=10)
        

        ### added - dmg - 2/2/04 ###
        displayStyle = {}
            
        self.scrTypeList = Tix.ScrolledHList(self.pInterior(1),
                                             options = \
                                             """
                                             hlist.width 65
                                             hlist.columns 4
                                             hlist.header 1
                                             hlist.selectMode single
                                             """
                                             )



        displayStyle['string'] = Tix.DisplayStyle('text',
                                                  refwindow=self.scrTypeList,
                                                  selectforeground='black',
                                                  activebackground = 'red',
                                                  #state='disabled',
                                                  background = self.pInterior(1).cget("background"),
                                                  anchor='w')
        
        displayStyle['checkbutton']  = Tix.DisplayStyle("window",
                                                        refwindow = self.scrTypeList,
                                                        background = self.pInterior(1).cget("background"),
                                                        )
        
        self.scrTypeList.pack(side='bottom', anchor='n', fill='x', expand=True, pady=15, padx=10)
        self.tList = self.scrTypeList.hlist
        self.tList.config(browsecmd=self.updateTypeDesc)
        self.tList.configure(background = self.pInterior(1).cget("background"))

        columnTitles = ["", "Type", "Extensions", "Current handler"] 
        columnTypes  = ['checkbutton', 'string', 'string', 'string']
        
        for i in range(len(columnTitles)):
            c = ColumnHeader(self.tList, columnTitles[i])
            self.tList.header_create(i, itemtype='window',
                                     window = c)
        
        ### END added ###

        fi = fileInfo
        self.types      = [ t for t in fi.types() if fi.mimeType(t) != None ]

        ## decided not to use this file type
        del self.types[self.types.index("Gaussian formatted checkpoint")]

        self.typeDescs = {}
        
        for t in self.types:
            try:
                self.typeDescs[t] = FileTypeDescs[t]
            except KeyError:
                self.typeDescs[t] = "No Description Available"

        self.handledBy  = [None] * len(self.types)
        self.check_vars = []


        ### ADDED dmg - 2/2/2004 ###

        ## columns should be checkbutton, type, extensions, handler

        val_map = {}
                
        for t in self.types:

            idx = self.types.index(t)

            val_map[idx] = []
    
            check_var = Tkinter.IntVar(self.pInterior(1))
            check_var.set(0)
            self.check_vars.append(check_var)
          

            ## check button for this row
            ck = Tkinter.Checkbutton(self.tList, variable = check_var)
            val_map[idx].append(ck)

            ## type label for this row...
            type_lbl       = t
            val_map[idx].append(type_lbl)

            ## extensions for this row
            ext_lbl   = "[ %s ]" % ( " , ".join(fi.extensions(t)) )
            val_map[idx].append(ext_lbl)


            mime_types = fileInfo.mimeType(t)
            exts       = fileInfo.extensions(t)
            cur_handler = self.ftm.getCurrentHandler(mime_types, exts)
            val_map[idx].append(cur_handler)
        
            
        for row in range(len(self.types)):
            self.tList.add(row)
            values = val_map[row]

            for col in range(len(values)):
                colType = columnTypes[col]
                if colType == 'string':
                    self.tList.item_create(row, col, text=values[col], style=displayStyle[colType])
                elif colType == 'checkbutton':
                    self.tList.item_create(row, col, itemtype='window', window=values[col],
                                           style=displayStyle[colType])

        #### END ADDED ############


    def createPanelThree(self):        
        self.createTitle(2, "Confirm")
        self.createExplanation(2, "You have chosen to use Chimera as the helper application "  \
                               "for the following file types:")


        t = Tkinter.Text(self.pInterior(2), relief = 'flat',
                           wrap = 'word',
                           pady=15,
                           height=3,
                           width=50)
        t.insert(0.0, "If this is OK, click 'Next' to continue, or click 'Back' and choose again")
        t.pack(side='bottom', anchor='nw', padx=10,
               fill='x', expand=True)
        t.configure(state='disabled', background=self.pInterior(2).cget('background'))

        
        #self.selected_frame = Tkinter.Frame(self.pFrames[2])
        self.selected_frame = Pmw.ScrolledFrame(self.pInterior(2),
                                                borderframe = 0,
                                                usehullsize = 1,
                                                hull_width = 450,
                                                hull_height = 175)
        
        self.sel_mime_labels = []
        
        self.selected_frame.pack(side='top', anchor = 'nw', padx=10,
                                 fill='x', expand=True)
        

        

    def createPanelFour(self):
        self.createTitle(3, "Browser Configuration")
        #self.createExplanation(3, self.configStatusString)

        ## contains results of config results
        self.config_res_text = Tkinter.Text(self.pInterior(3), relief = 'flat',
                                     wrap = 'word',
                                     pady=15,
                                     height=3,
                                     width=50)
        
        self.config_res_text.pack(side='top', anchor='nw', padx=10,
                                  fill='x', expand=True)
        self.config_res_text.configure(state="disabled", background=self.pInterior(3).cget('background'))


        self.closing_text = Tkinter.Text(self.pInterior(3), relief = 'flat',
                                         wrap = 'word',
                                         pady=15,
                                         height=3,
                                         width=50)

        self.closing_text.pack(side='bottom', anchor='nw', padx=10,
                               fill='x', expand=True)
        self.closing_text.configure(state="disabled", background=self.pInterior(3).cget('background'))
        

        #self.config_res_frame = Tkinter.Frame(self.pFrames[3])
        self.config_res_frame = Pmw.ScrolledFrame(self.pInterior(3),
                                                  borderframe = 0,
                                                  usehullsize = 1,
                                                  hull_width = 450,
                                                  hull_height = 175)

        self.res_labels = []
        self.config_res_frame.pack(side='top', anchor='nw', padx=10,
                                   fill='x', expand=True)


    def updateTypeDesc(self, event=None):
        s = self.tList.info_selection()
        #print "S IS ", s
        
        self.desc_txt.configure(state="normal")
        self.desc_txt.delete(0.0, Tkinter.END)
        self.desc_txt.insert(0.0, self.typeDescs[self.types[int(s[0])]])
        self.desc_txt.configure(state="disabled")

    def popMimeSelFrame(self):
        
        for i in range(len(self.sel_mime_labels)):
            #print "forgetting ", self.sel_mime_labels[i].cget("text")
            (self.sel_mime_labels[i]).grid_forget()

        self.sel_mime_labels = []

        
        idx = 0
        if 1 in [cv.get() for cv in self.check_vars]:
            for i in range(len(self.check_vars)):
                if self.check_vars[i].get():
                    lbl = Tkinter.Label(self.selected_frame.interior(),
                                        text=self.types[i], font=("arial", 10, 'bold'))
                    lbl.grid(row=idx, column=0, sticky='w')
                    self.sel_mime_labels.append(lbl)
                    idx = idx + 1
        else:
            lbl = Tkinter.Label(self.selected_frame.interior(),
                                text="No file types selected", font=('arial', 10, 'bold'))
            lbl.grid(row=idx, column=0, sticky='w')
            self.sel_mime_labels.append(lbl)


    def registerFileAssn(self):
        requested = {}

        for idx in range(len(self.check_vars)):
            if self.check_vars[idx].get() == 1:
                requested[self.types[idx]] = False

        for desc in requested.keys():
            ## here mimetype is a list of mimetypes
            mimetypes = fileInfo.mimeType(desc)
                                        
            exts = fileInfo.extensions(desc)
            
            for mime in mimetypes:
                print "registering file association for (%s) (%s) (%s)" % (desc, exts, mime)
                requested[desc] = self.ftm.registerFileAssn( desc, exts, mime ) 

                
        #print "after trying to register, got: "
        #import pprint
        #pprint.pprint(requested)

        res_msg = ''
        
        
        if [res for res in requested.values() if res==False]:
            b4_res_msg = "Sorry!  An error occurred while while configuring the\n" \
                         "following file types:\n\n"
            after_res_msg = "Try configuring your system manually using the\n" \
                            "instructions given in the Chimera documentation.\n\n" \
                            "Click 'Finish' to continue..."
            all_ok = False
            #res_msg += "\n".join( ([type for type in requested.keys() if requested[type]==False]))
        else:
            b4_res_msg = "Congratulations!! Your system  has been successfully" \
                      "configured to open the following file types with Chimera: \n\n"

            after_res_msg = "Click 'Finish' to continue..."

            all_ok = True
            #res_msg += "\n".join( ([type for type in requested.keys() if requested[type]==True]))

        self.popConfigResFrame( b4_res_msg, after_res_msg, [type for type in requested.keys() if requested[type]==all_ok] )
        
    def popConfigResFrame(self, b4_msg, after_msg, types):

        self.config_res_text.configure(state='normal')
        self.config_res_text.delete(0.0, Tkinter.END)
        self.config_res_text.insert(0.0, b4_msg)
        self.config_res_text.configure(state='disabled')
        
        for l in self.res_labels:
            l.grid_forget()

        self.res_labels = []

        idx=0
        
        if types:
            for type in types:
                lbl = Tkinter.Label(self.config_res_frame.interior(),
                                    text=type, font=('arial', 10, 'bold'))
                lbl.grid(row=idx, column=0, sticky='w')
                self.res_labels.append(lbl)
                idx = idx + 1
        else:
            lbl = Tkinter.Label(self.config_res_frame.interior(),
                                text="No file types configured", font=('arial', 10, 'bold'))
            lbl.grid(row=idx, column=0, sticky='w')
            self.res_labels.append(lbl)

        self.closing_text.configure(state='normal')
        self.closing_text.delete(0.0, Tkinter.END)
        self.closing_text.insert(0.0, after_msg)
        self.closing_text.configure(state='disabled')


    def Next(self):

        if self.pCurrent == 1:
            self.popMimeSelFrame()
        elif self.pCurrent == 2:
            self.registerFileAssn()

        WizShell.Next(self)
        
    
class ColumnHeader(Tkinter.Frame):

	def __init__(self, master, title, **kw):
		try:
			self.colCmd = kw["command"]
		except KeyError:
			self.colCmd = None
		else:
			del kw["command"]
		kw["takefocus"] = 1
		Tkinter.Frame.__init__(self, master, **kw)
		self.colTitle = Tkinter.Label(self, text=title)
		self.colTitle.pack(side=Tkinter.LEFT)
		self.colImage = None
		if self.colCmd:
			self.colTitle.bind("<ButtonRelease>", self.colCmd)

	#def setTitle(self, title):
	#	self.colTitle.config(text=title)
#
	#def setImage(self, img):
	#	if img is None:
	#		if self.colImage:
	#			self.colImage.destroy()
	#			self.colImage = None
	#	else:
	#		if self.colImage:
	#			self.colImage.config(image=img)
	#		else:
	#			self.colImage = Tkinter.Label(self, image=img)
	#			self.colImage.pack(side=Tkinter.RIGHT)
	#			if self.colCmd:
	#				self.colImage.bind("<ButtonRelease>",
	#							self.colCmd)
