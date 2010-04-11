import chimera
from chimera.baseDialog import ModelessDialog

import Tkinter


class WizShell(ModelessDialog):
    """This class represents a 'Wizard' pattern, a graphical user
    interface containing multiple panels, with 'Next' and 'Back' buttons
    that allow the user to navigate through the panels. In addition to
    the buttons on the bottom of the dialog, the left hand-side can
    contain an image, the top can contain a title, and the rest of the
    space is reserved for each individual panel.
    The following diagram illustrates this layout:

    __________________________
    |    |  2                |
    |    |  ________________ |
    |    | |  2a            ||
    |    | |----------------||
    |  1 | |  2b            ||
    |    | |________________||
    |    |                   |
    |    |                   |
    |    |                   |
    |    |                   | 
    |____|___________________|


    1. This area (Tkinter.Frame) contains an image (specified by the img_src
       argument to __init__ )
       WizShell will not clip the image at all, but just use it 'as-is'
       Therefore, for the best aesthetic appearance, use an image that has
       approximately a 1:2 to 1:3 ration, where the width of the image
       is no more than 1/3 the resultant panel width,
       and the height of the image is between one and two times the
       resultant panel height. Note that the inclusion of different size widgets
       may cause the WizShell to stretch beyond the width and height
       defined in __init__ (see below). Ultimately, finding an image that fits
       well will be a matter of trial and error - these are just general
       guidlines

    2. This area (Tkinter.Frame) is reserved for 'panels.' A panel can contain
       whatever widgets the developer wants. The WizShell does offer some conveniences
       though, to make development easier and give this widget a similar L&F across
       instances:

    2a. This area can contain a title (Tkinter.Label) for that particular panel, in bold letters.
        It can be created by calling createTitle(n,t) where n is the panel number
        (zero-indexed) for which you want to create the title, and t is the actual
        text of the title

    2b. This are can contain an explanation for that particular panel. This is usually
        a short, 2-3 sentence description (in a 3-line Tkinter.Text widget) of the purpose
        of that particular panel. This explanation can be added to a panel by calling
        createExplanation(n,e), where n is the panel number (zero-indexed), and e in the
        text for  the desired explanation

    Note: if their corresponding create functions are not called, the widgets described
    in 2a and 2b will not be created, essentially giving more space for whatever
    content the panel is intended to contain. 

    When building your panels, you should use the pInterior(n) method, where n is
    the number (zero-indexed) of the panel you are accessing. This method returns
    a reference to the actual panel that will be packed into area (2) in the
    above diagram. This reference can be used to pack additional widgets, or
    modify existing child widgets for that panel.
    
    """

    
    buttons = ('Back', 'Next', 'Cancel')
    provideStatus = False

    def __init__(self, num, width, height, img_src, **kw):
        """num is the number of panels the wizard is to contain
        width is the desired width of each panel, in pixels
        height is the desired height of each panel, in pixels
        img_src is the absolute path to a .gif file containing
        an image to appear in the left-hand side of the wizard
        """

        self.panel_width = width
        self.panel_height = height

        self.img_src = img_src
        
        if kw.has_key('img_bg_color'):
            self.img_bg_color = kw['img_bg_color']
        else:
            self.img_bg_color = None
        
        self.numPanels = num
        self.pCurrent = 0
        self.pFrames =  [None] * self.numPanels
        
        ModelessDialog.__init__(self)


    def fillInUI(self, parent):

        #self.small_font   = self.makeSmallFont()
        #self.bigbold_font = self.makeBigBoldFont()


        ## Tk nonsense to make the font small (but maintain other characteristics)
        dummy_label = Tkinter.Label(parent, text="foo")
        font = dummy_label.cget('font')
        font = chimera.tkgui.app.tk.call('font', 'actual', font)
        font_list = list(font)
        del dummy_label


        ## make a smaller-sized font
        small_font = font_list[:]
        
        try:
            size_idx = small_font.index('-size')+1
            small_font[size_idx] = int( .9 * int(small_font[size_idx]) )
        except ValueError:
            pass

        try:
            weight_idx = small_font.index('-weight')+1
            small_font[weight_idx] = 'normal'
        except ValueError:
            pass
            
        self.small_font = tuple(small_font)

        ## make a bigger bolder font
        bigbold_font = font_list[:]
        
        try:
            bigbold_font[bigbold_font.index('normal')] = 'bold'  
        except ValueError:
            pass
         
        try:
            size_idx = bigbold_font.index('-size')+1
            num      = int( 1.5 * int(bigbold_font[size_idx]) )
            next_num = num+1
            bigbold_font[size_idx] = (num,next_num)[num%2!=0]
        except ValueError:
            pass
            
        self.bigbold_font = tuple(bigbold_font)
        ########################################

        
        self.setUpFrames(parent)
        
        # add the image on the left
        self.addImg()
  
        self.__createFrames()

        self.buttonWidgets['Back'].configure(state='disabled')

        ## added to account for the case where wizard has only one panel
        if self.pCurrent == self.numPanels - 1:
            self.buttonWidgets['Next'].configure(text='Finish', command=self.Cancel)

        self.updateCounter()

    def pInterior(self, idx):
        """idx is the number (zero-indexed) of the panel you want a
        to get a reference to. Returns a reference to that panel
        """
        
        return self.pFrames[idx]


    def __createFrames(self):
        """this function creates the requested number of panels, each
        having the requested width and height, as passed to the
        __init__ function
        """

        for i in range(self.numPanels):
            self.pFrames[i] = Tkinter.Frame(self.panelFrame, width=self.panel_width,
                                            height=self.panel_height)

            if not i == self.pCurrent:
                self.pFrames[i].forget()
            else:
                self.pFrames[i].pack(fill='both', expand=True)
        
    def setUpFrames(self, parent):
        """sets up the two main frames in the function.
        imgFrame, located on the left (1 in above diagram), will
        contain the image passed in to __init__ .
        panelFrame, located on the right (2 in above diagram),
        is just a contained that will hold each panel as it is
        packed
        """

        self.imgFrame   = Tkinter.Frame(parent)
        self.panelFrame = Tkinter.Frame(parent, width=self.panel_width,
                                        height=self.panel_height, relief='flat')
        self.countFrame = Tkinter.Frame(parent, relief='flat')

        self.imgFrame.pack(side='left', fill='y') ## dont expand here...
        self.panelFrame.pack(side='top', fill='both', expand=True)
        self.countFrame.pack(side='bottom', fill='x')

        ## add the counter
        self.panelCountVar = Tkinter.StringVar(parent)
        self.panelCountVar.set("")
        self.panelCountLabel = Tkinter.Label(self.countFrame,
                                           textvariable=self.panelCountVar,
                                           font=self.small_font
                                           )
        self.panelCountLabel.pack(side='right', pady=5, padx=10)
        
        
    def addImg(self):

        if self.img_bg_color:
            try:
                self.imgFrame.configure(background=self.img_bg_color)
            except Tkinter.TclError:
                pass
        
        from chimera import chimage
        self._wizImage = chimage.get(self.img_src, self.imgFrame)

        self._wizLabel = Tkinter.Label(self.imgFrame, image=self._wizImage, borderwidth=0)
        self._wizLabel.__image = self._wizImage
        
        self._wizLabel.pack(side='left', anchor='n')


    def createTitle(self, idx, title):
        """This function should be called by code that subclasses WizShell.
        It creates a title Label widget in area 2a in the above diagram.
        'idx' is the number of the panel (zero-indexed) in which to create
        the title
        'title' is a string representing the actual text of the Label
        """

        lab = Tkinter.Label(self.pFrames[idx], text=title,
                            font=self.bigbold_font, relief='flat', 
                            padx=10, pady=15)
        lab.pack(side='top', fill='x', anchor='w')

    def createExplanation(self, idx, exp, **kw):
        """This function should be called by code that subclasses WizShell.
        It creates a Text widget in area 2b in the above diagram.
        'idx' is the number of the panel (zero-indexed) in which to create
        the explanation
        'exp' is a string representing the actual text of the explanation
        """
        if not kw.has_key('width') : kw['width']=50
        if not kw.has_key('height'): kw['height']=4

        txt = Tkinter.Text(self.pFrames[idx],
                           relief = 'flat',
                           wrap = 'word',
                           padx=5,
                           pady=5,
                           **kw
                           )

        txt.insert(0.0, exp)
        txt.pack(side='top', anchor= 'nw', padx=10, expand=False, fill='x')
        txt.configure(state='disabled', background=self.pFrames[idx].cget('background'))
      

    def getCurrentPanel(self):
        """returns the current panel number (zero-indexed)
        """
        return self.pCurrent

    def isLastPanel(self):
        """return True if the wizard is currently on the last panel,
        else return False
        """
        return (self.pCurrent == (self.numPanels-1))

    def isFirstPanel(self):
        """return True if the wizard is currently on the first panel,
        else return False
        """
        return self.pCurrent == 0

    def Restart(self):
        current_panel = self.pCurrent
        self.pCurrent = 0

        self.buttonWidgets['Back'].configure(state='disabled')

        self.pFrames[current_panel].forget()
        self.pFrames[self.pCurrent].pack(fill='both', expand=True)

        self.updateCounter()
    
    def Next(self):
        """This function is invoked when the 'Next' button is clicked on the wizard.
        Classes which inherit from WizShell will probably want to override this function,
        to actually do something besides displaying different text when the 'Next' button
        is pushed, but *BE SURE THAT YOU CALL THIS FUNCTION* at some point in your 'Next' function.
        This code takes care of packing and unpacking the necessary panes, and dynamically
        assigning text and functionality to buttons as necessary
        """
        
        current_panel = self.pCurrent        
        self.pCurrent = self.pCurrent + 1

        ## is this necessary here?
        self.buttonWidgets['Back'].configure(state='normal')

        ## or this ?!?
        if self.pCurrent == self.numPanels - 1:
            self.buttonWidgets['Next'].configure(text='Finish', command=self.Cancel)
        
        self.pFrames[current_panel].forget()
        self.pFrames[self.pCurrent].pack(fill='both', expand=True)

        self.updateCounter()

    def Back(self):
        """This function is invoked when the 'Back' button is clicked on the wizard.
        Once again, classes that inherit from WizShellm ay want to override this
        function, but be sure to call this at some point in your subclass' 'Back'
        function
        """
        current_panel = self.pCurrent
        self.pCurrent -= 1

        if self.pCurrent <= 0:
            self.pCurrent=0
            self.buttonWidgets['Back'].configure(state='disabled')

        if current_panel == self.numPanels - 1:
            self.buttonWidgets['Next'].configure(text='Next', command=self.Next)

        self.pFrames[current_panel].forget()
        self.pFrames[self.pCurrent].pack(fill='both', expand=True)

        self.updateCounter()

    def updateCounter(self):
        self.panelCountVar.set("%d of %d" % ((self.pCurrent+1),self.numPanels))

