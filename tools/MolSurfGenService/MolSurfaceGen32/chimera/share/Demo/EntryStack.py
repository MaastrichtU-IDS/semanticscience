import Pmw, Tkinter
from chimera import chimage, help


class EntryStack(Tkinter.Frame):

    def __init__(self, parent):

        Tkinter.Frame.__init__(self, parent)
        
        self.row_count = 0
        self.row_widgets = []

        self.doUI(parent)


    def doUI(self, parent):
        
        self.scrFrame = Pmw.ScrolledFrame(self, frame_relief='sunken',
                                          horizflex='expand')
	self.scrFrame.grid(row=0, column=0,padx=5, columnspan=2, sticky='nsew')
        self.rowFrame = self.scrFrame.component('frame')
        	
	self.addB = Tkinter.Button(self, command=self._addCB)
        plus_image = chimage.get("plus.gif",self.addB)
        self.addB.configure(image=plus_image)
        self.addB._image = plus_image
        help.register(self.addB, balloon="Add a row below currently selected row")
	self.addB.grid(row=1,column=0,pady=5,padx=0,sticky='n')

        
	self.delB = Tkinter.Button(self, command=self._delCB)
        minus_image = chimage.get("minus.gif",self.delB)
        self.delB.configure(image=minus_image)
        self.delB._image = minus_image
        help.register(self.delB, balloon="Delete the currently selected row")
	self.delB.grid(row=1,column=1,pady=5,padx=0,sticky='nw')
        self.delB.configure(state="disabled")
        
        self.rowconfigure(0, weight=10)
        self.rowconfigure(1, weight=0)

        self.columnconfigure(1, weight=10)


    def _addCB(self):

        entry_idx = self.getActiveIdx()
        if entry_idx != None:
            insert_idx = entry_idx + 1
        else:
            insert_idx = self.row_count

        #print "insert_idx is ", insert_idx
        checkVar, checkB, entry = \
                     self.makeRow()


        ## need to ungrid all the rows after this one, then regrid it
        ## off by one

        for idx in range(insert_idx, self.row_count):
            #print "moving %s to %s" % (idx,idx+1)
            c, v, e = self.row_widgets[idx]
            c.grid_remove()
            c.grid(row=idx+1, column=0)
            e.grid_remove()
            e.grid(row=idx+1, column=1, sticky='ew')
        
	checkB.grid(row=insert_idx,column=0)
	entry.grid(row=insert_idx,column=1,sticky='ew')
        entry.focus_set()
        
	
	self.rowFrame.rowconfigure(self.row_count, weight=1)
	self.rowFrame.columnconfigure(1,weight=1)
	
        self.row_widgets.insert( insert_idx, (checkB,checkVar,entry) )
        self.row_count += 1
        self.delB.configure(state="normal")

        self.scrFrame.yview('moveto',1.0)
        #print self._toplevel.focus_get()

    def addRow(self, active=None, content=None):
        self._addCB()

        idx = self.getActiveIdx() or self.row_count-1

        checkb, var, entry = self.row_widgets[idx]

        if active != None:
            var.set([0,1][active])
        if content != None:
            entry.insert(0,content) 


    def _delCB(self): 
	if self.row_count == 0: 
	    return

        entry_idx = self.getActiveIdx()
        #print "got %s for entry_idx" % entry_idx

        if entry_idx != None:
            #print "entry_idx is ", entry_idx
            rm_idx = entry_idx
        else:
            rm_idx = self.row_count-1
            #print "using default rm_idx ", self.row_count-1

        #print "rm_idx is ", rm_idx

        checkB, checkVar, entry = self.row_widgets[rm_idx]
	
	checkB.grid_remove()
	entry.grid_remove()
        del checkB, entry

        ## need to bring all the subsequent commands up one
        ## index
        for idx in range(rm_idx+1, self.row_count):
            c, v, e = self.row_widgets[idx]
            #print "moving %s to %s" % (idx,idx-1)
            c.grid_remove()
            c.grid(row=idx-1, column=0)
            e.grid_remove()
            e.grid(row=idx-1, column=1, sticky='ew')

	self.rowFrame.rowconfigure(self.row_count,weight=1)

        del self.row_widgets[rm_idx]
        self.row_count -= 1

        if self.row_count > 0:
            self.row_widgets[-1][2].focus_set()
        else:
            self.delB.configure(state="disabled")
            

    def makeRow(self):
        checkVar = Tkinter.IntVar()
        checkVar.set(1)
        
	checkB = Tkinter.Checkbutton(self.rowFrame, variable=checkVar)
	entry  = Tkinter.Entry(self.rowFrame)

        return checkVar, checkB, entry


    def getActiveIdx(self):
        cur_focus_widg = self.focus_get()

        for i,entry_w in enumerate(self.row_widgets):
            if cur_focus_widg == entry_w[2]:
                return i
        else:
            return None


    def getRows(self):

        row_data = []

        for r in self.row_widgets:
            button, var, entry = r
            row_data.append( (var.get(), entry.get()) )

        return row_data
