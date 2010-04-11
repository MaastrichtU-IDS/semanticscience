from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw

import chimera
from chimera import tkoptions
from chimera import chimage
from chimera import help

import tempfile, os, sys, string

from MovieRecorder import getTruncPath, DEFAULT_OUTFILE, EXIT_SUCCESS, EXIT_ERROR, EXIT_CANCEL
from MovieRecorder import getRandomChars, DEFAULT_PATTERN
from MovieRecorder import MovieError
from MovieRecorder import RESET_CLEAR, RESET_KEEP, RESET_NONE
from MovieRecorder import BaseRecorderGUI

FRM_OPTS_ROW = 6
MOV_OPTS_ROW   = 8

# Formats: (description, file suffix, ffmpeg format name, ffmpeg video codec,
#           limited frame rates)
formats = [
    ('MPEG-1', 'mpg', 'mpeg1video', None, True),
    ('MPEG-2', 'mpg', 'mpeg2video', None, True),
    ('MPEG-4', 'mp4', 'mp4', None, False),
    ('AVI MSMPEG-4v2', 'avi', 'avi', 'msmpeg4v2', False),
    ('Quicktime', 'mov', 'mov', None, False),
#    ('Animated GIF', 'gif', 'gif', None, False),
    ]
file_suffix_field = 1
file_format_field = 2
video_codec_field = 3
limited_frame_rate_field = 4
default_format = formats[4]
descrip2format = {}
for fmt in formats:
    descrip2format[fmt[0]] = fmt

# Movie command format names.
command_formats = {'mpeg': descrip2format['MPEG-1'],
                   'mp2': descrip2format['MPEG-2'],
                   'mp4': descrip2format['MPEG-4'],
                   'avi': descrip2format['AVI MSMPEG-4v2'],
                   'mov': descrip2format['Quicktime'],
#                   'gif': descrip2format['Animated GIF'],
                   }

imageFormats = ('JPEG', 'PNG', 'PPM')
defaultImageFormat = 'PPM'
raytraceImageFormats = ('PNG',)
defaultRaytraceImageFormat = 'PNG'
    
## Resolution presets
VCD  = "VCD"
SVCD = "SVCD"
DVD  = "DVD"

## Descriptions

standard_formats = {
    VCD: {'resolution': (352,240),
          'format'    : descrip2format["MPEG-1"],
          'bit_rate'  :  1150,
          'buf_size'  :  40
          },

    SVCD: {'resolution': (480,480),
          'format'    :  descrip2format["MPEG-2"],
          'bit_rate'  :  2040,
          'buf_size'  :  224
          },

    DVD: {'resolution': (720,480),
          'format'    : descrip2format["MPEG-2"],
          'bit_rate'  : 6000,
          'buf_size'  : 224
          }
    }

default_bit_rate = 2000         # kbits/sec
default_buffer_size = 200       # kbytes

menu_formats = map(lambda fmt: '%s [.%s]' % fmt[:2], formats)
menu_values = formats

class MovieFmtTkOption(tkoptions.SymbolicEnumOption):
    labels = menu_formats
    values = menu_values


class MovieRecorderGUI(ModelessDialog,BaseRecorderGUI):
    name = "Movie Recorder"
    buttons = ('Close')
    provideStatus = True
    help = "ContributedSoftware/recorder/recorder.html"

    def __init__(self):

        self.director = None
        
        self.this_dir = os.path.split(os.path.abspath(__file__))[0]
        
        ModelessDialog.__init__(self)

        self.cache_width  = None
        self.cache_height = None

        ## get the width and height when the frame options are expanded
        self.frmOptionsFrame.grid(row=FRM_OPTS_ROW ,column=0, columnspan=3, sticky='nsew')
        chimera.tkgui.app.update_idletasks()
        self.frm_width, self.frm_height = \
                        (self.frmOptionsFrame.winfo_width(), self.frmOptionsFrame.winfo_height())
        self.frmOptionsFrame.grid_forget()
        chimera.tkgui.app.update_idletasks()


        ## get the width and height when the movie options are expanded
        self.movOptionsFrame.grid(row=MOV_OPTS_ROW,column=0, columnspan=3, sticky='nsew')
        chimera.tkgui.app.update_idletasks()
        self.mov_width, self.mov_height = \
                        (self.movOptionsFrame.winfo_width(), self.movOptionsFrame.winfo_height())
        self.movOptionsFrame.grid_forget()
        chimera.tkgui.app.update_idletasks()

        w,h = map(int,self.getCurrentDimensions())
        self._toplevel.wm_geometry('%sx%s' % (w+30,h+20))
        
        #self.director.adjustGfxSize()

        chimera.tkgui.app.after(1000, self.showStatus, "Click the record button to start capturing frames")

    def fillInUI(self, parent):
        #recCtrlFrame = Tkinter.Frame(parent)
        #recCtrlFrame.grid(row=0,column=0,columnspan=2, sticky='w', pady=10, padx=10)


        ##--------Record button-----------##
        self.recButton = Tkinter.Button(parent, text="Record", command=self.startRecording)
        #self.rec_img   = chimage.get(os.path.join(self.this_dir, "record.png"), self.recButton)
        #self.pause_img = chimage.get(os.path.join(self.this_dir, "pause.png"),  self.recButton)
        #self.recButton.configure(image=self.rec_img, relief='flat')
        #self.recButton._rec_image   = self.rec_img
        #self.recButton._pause_image = self.pause_img
        help.register(self.recButton,   balloon="Start capturing frames from the graphics window")
        self.recButton.grid(row=0,column=0, sticky='w', pady=5, padx=10)
        ## ---------------------------------

            

        ##--------Encode button-----------##
        self.encButton = Tkinter.Button(parent, text="Make movie", command = self.startEncoding)
        #self.movie_img = chimage.get(os.path.join(self.this_dir, "movie.png"),        self.encButton)
        #self.abort_img = chimage.get(os.path.join(self.this_dir, "abort_movie.png"),  self.encButton)

        #self.encButton.configure(image=self.movie_img, relief='flat')
        #self.encButton._movie_img  = self.movie_img
        #self.encButton._abort_img  = self.abort_img
        help.register(self.encButton,   balloon="Make a movie from currently captured frames")
        
        self.encButton.grid(row=0,column=1, sticky='w')

        ## can't encode yet - don't have any frames cached !
        self.encButton.configure(state='disabled')
        ## ------------------------------------



        ##--------Reset button-----------##
        self.clearButton = Tkinter.Button(parent,
                                          text="Reset",
                                          command=self.resetRecording)
        help.register(self.clearButton, balloon="Clear all saved frames")
        self.clearButton.configure(state='disabled')
        self.clearButton.grid(row=1, column=0, sticky='w', pady=5, padx=10)
        ## ---------------------------------



        ## ------Reset after encode-------------
        self.autoResetVar = Tkinter.IntVar(parent)
        self.autoResetVar.set(1)

        autoResetChB = Tkinter.Checkbutton(parent,
                                           text="Reset after encode",
                                           variable = self.autoResetVar,
                                           command  = self.resetModeCB
                                           )
        autoResetChB.grid(row=1,column=1, sticky='w')
        ## -------------------------------------



        
        #-------Movie format---------------------------
        self.movieFmtOption = MovieFmtTkOption(parent,
                                               2, 'Output format',
                                               default_format,
                                               self.chooseFmtCB)
        ## ------------------------------------------------


        
        ## -------------Output path ------------------
        outputFrame = Tkinter.Frame(parent)
        from OpenSave import tildeExpand
        initialfile = os.path.join(tildeExpand("~"), DEFAULT_OUTFILE)

        from OpenSave import SaveModeless
        class OutputPathDialog(SaveModeless):
            default = 'Set Movie Path'
            title = 'Select movie output file'
            def SetMoviePath(self):
                self.Save()
        setattr(OutputPathDialog, OutputPathDialog.default,
                OutputPathDialog.SetMoviePath) # Work around OpenSave bug
        ofo = tkoptions.OutputFileOption(outputFrame,
                                         0, 'Output file',
                                         initialfile,
                                         None,
                                         balloon = 'Output file save location '
                                         )
        ofo.dialogType = OutputPathDialog
        self.outFileOption = ofo
        outputFrame.grid(row=3, column=0, columnspan=3, sticky='ew', pady=10)
        outputFrame.columnconfigure(1, weight=1)
        ## -------------------------------------------
        

        

    
        statsGroup = Pmw.Group(parent, tag_text="Status")
        statsGroup.grid(row=0, column=2, rowspan=3, padx=20, sticky='nsew')
        #statsGroup.configure(hull_width=1000)
        
        self.frame_num_var = Tkinter.StringVar(parent)
        self.time_left_var = Tkinter.StringVar(parent)

        self.actionLabel    = Tkinter.Label(statsGroup.interior(), text="Stopped")
        numFramesLabel = Tkinter.Label(statsGroup.interior(),
                                       text = "# Frames:")#,

        frameResLabel = Tkinter.Label(statsGroup.interior(),
                                      text = "Resolution:")#,

        estLengthLabel = Tkinter.Label(statsGroup.interior(),
                                       text = "Est. Length:")#,

        #statsGroup.interior().rowconfigure(0,weight=1)
        statsGroup.interior().columnconfigure(2,weight=1)

        self.accum_frames_var = Tkinter.StringVar(parent)
        self.accum_frames_var.set('0')

        self.frame_res_var = Tkinter.StringVar(parent)
        self.frame_res_var.set('%dx%d' % chimera.viewer.windowSize)
        
        self.accum_secs_var   = Tkinter.StringVar(parent)
        self.accum_secs_var.set('0s.')

        
        numFramesVal = Tkinter.Label(statsGroup.interior(),
                                     textvariable = self.accum_frames_var)

        frameResVal = Tkinter.Label(statsGroup.interior(),
                                     textvariable = self.frame_res_var)
        
        estLengthVal = Tkinter.Label(statsGroup.interior(),
                                     textvariable = self.accum_secs_var)
        
        self.actionLabel.grid(row=0,column=0, columnspan=2, pady=2, sticky='w')
        numFramesLabel.grid(row=1,column=0, pady=2, sticky='w')
        frameResLabel.grid(row=2, column=0, pady=2, sticky='w')
        estLengthLabel.grid(row=3, column=0, pady=2, sticky='w')

        numFramesVal.grid(row=1, column=1, padx=5, sticky='w')
        frameResVal.grid(row=2, column=1, padx=5, sticky='w')
        estLengthVal.grid(row=3, column=1, padx=5, sticky='w')

        
        parent.columnconfigure(2, weight=1)
        parent.columnconfigure(3, weight=2)
        parent.rowconfigure(9, weight=1)

        dummyFrame = Tkinter.Frame(parent, relief='groove', borderwidth=1)
        Tkinter.Frame(dummyFrame).pack()
        dummyFrame.grid(row=4,column=0,columnspan=3, pady=10, sticky='ew')

        ## -------------- Frame options -----------------------
        frmOptChBFrame = Tkinter.Frame(parent, background="gray")
        frmOptChBFrame.grid(row=5, column=0,columnspan=3, pady=5, sticky='ew')
        frmOptChBFrame.columnconfigure(1, weight=1)

        self.frmOptionsVar = Tkinter.IntVar(frmOptChBFrame)
        frmOptionsChB = Tkinter.Checkbutton(frmOptChBFrame,
                                            indicatoron=False,
                                            selectcolor='',
                                            background="gray",
                                            offrelief='flat',
                                            overrelief='flat',
                                            text = "Options...",
                                            relief='flat',
                                            variable=self.frmOptionsVar,
                                            command = self.showFrmOptionsCB)

        r_arrow_img=chimage.get("rightarrow.png", frmOptionsChB)
        frmOptionsChB.configure(image=r_arrow_img)
        frmOptionsChB._image = r_arrow_img

        d_arrow_img=chimage.get("downarrow.png", frmOptionsChB)
        frmOptionsChB.configure(selectimage=d_arrow_img)
        frmOptionsChB._selectimage = d_arrow_img

        #frmOptionsChB.configure(relief='sunken')
        #print frmOptionsChB.configure().keys()
        frmOptionsChB.grid(row=0, column=0, sticky='w')

        frmOptionsLabel = Tkinter.Label(frmOptChBFrame, text="Frame Options", background="gray")
        frmOptionsLabel.grid(row=0,column=1, sticky='w', padx=5)

        self.frmOptionsFrame = Tkinter.Frame(parent)
        self.populateFrmOptionsFrame()
        ## ---------------------------------------------------
        
        
        ## --------------------- Movie options -----------------

        movOptChBFrame = Tkinter.Frame(parent, background="gray")
        movOptChBFrame.grid(row=7, column=0,columnspan=3, pady=5, sticky='ew')
        movOptChBFrame.columnconfigure(1, weight=1)

        self.movOptionsVar = Tkinter.IntVar(movOptChBFrame)
        movOptionsChB = Tkinter.Checkbutton(movOptChBFrame,
                                            indicatoron=False,
                                            selectcolor='',
                                            background="gray",
                                            offrelief='flat',
                                            overrelief='flat',
                                            text = "Options...",
                                            relief='flat',
                                            variable=self.movOptionsVar,
                                            command = self.showMovOptionsCB)

        movOptionsChB.configure(image=r_arrow_img)
        movOptionsChB._image = r_arrow_img

        movOptionsChB.configure(selectimage=d_arrow_img)
        movOptionsChB._selectimage = d_arrow_img

        movOptionsChB.grid(row=0, column=0, sticky='w', pady=0)

        movOptionsLabel = Tkinter.Label(movOptChBFrame, text="Movie Options", background="gray")
        movOptionsLabel.grid(row=0,column=1, sticky='w', padx=5)

        
        self.movOptionsFrame = Tkinter.Frame(parent)
        self.populateMovOptionsFrame()
        self.movOptionsFrame.columnconfigure(0, weight=1)
        ## -----------------------------------------------------


    def populateFrmOptionsFrame(self):

        #inputOptsGroup = Pmw.Group(self.optionsFrame, tag_text="Frame capture options")
        #inputOptsGroup.grid(row=0, column=0, sticky='nsew', pady=10)
        
        self.inputDirOption = tkoptions.InputFileOption(self.frmOptionsFrame,
                                                      0, 'Directory',
                                                      tempfile.gettempdir(), None,
                                                      balloon = 'Directory to use for saving image files',
                                                      dirsOnly=True
                                                      )

        self.inputPatternOption = tkoptions.StringOption(self.frmOptionsFrame,
                                                         1, 'Filename pattern',
                                                         DEFAULT_PATTERN % getRandomChars()
                                                         , None)
        
        class ImgFmtTkOption(tkoptions.SymbolicEnumOption):
            labels=['%s [.%s]' % (f, f.lower()) for f in imageFormats]
            values=imageFormats
            
        self.imgFmtOption = ImgFmtTkOption(self.frmOptionsFrame,
                                           2, 'Format',
                                           defaultImageFormat, None)

        ssf = Tkinter.Frame(self.frmOptionsFrame)
        ssf.grid(row=3, column=0, columnspan=2, sticky='w')

        self.useSuperSampleVar = Tkinter.IntVar(self.frmOptionsFrame)
        ssb  = Tkinter.Checkbutton(ssf, variable=self.useSuperSampleVar,
                                   text='Supersample')
        ssb.grid(row=0, column=0, sticky='w')
        self.superSampleButton = ssb

        from chimera.printer import SupersampleOption
        self.superSampleOption = SupersampleOption(ssf, 0, '',
                                                   3, None, startCol=1)

        rtf = Tkinter.Frame(self.frmOptionsFrame)
        rtf.grid(row=4, column=0, columnspan=2, sticky='w')

        self.raytraceVar = Tkinter.IntVar(self.frmOptionsFrame)
        rtb  = Tkinter.Checkbutton(rtf, variable=self.raytraceVar,
                                   text="Raytrace with POV-Ray",
                                   command=self.raytraceCB)
        rtb.grid(row=0, column=0, sticky='w')
        self.raytraceButton = rtb

        rto = Tkinter.Button(rtf, text='Options',
                             command=self.raytraceOptionsCB)
        rto.grid(row=0, column=1, sticky='w')

        self.keepSrcVar = Tkinter.IntVar(self.frmOptionsFrame)
        keepSrcChB  = Tkinter.Checkbutton(self.frmOptionsFrame,
                                          variable=self.keepSrcVar,
                                          text="Save images on Reset",
                                          command=self.resetModeCB)
        keepSrcChB.grid(row=5, column=0, columnspan=2, sticky='w')

        self.frmOptionsFrame.columnconfigure(1,weight=1)


    def populateMovOptionsFrame(self):
    
        ##-------------Quality params---------------------

        mof = Tkinter.Frame(self.movOptionsFrame)
        mof.grid(row=1,column=0,sticky='w')

        h = Tkinter.Label(mof, text='Bit rate controls quality and file size:')
        h.grid(row=0, column=0, sticky = 'w')

        brf = Tkinter.Frame(mof)
        brf.grid(row=1,column=0,sticky='w')
        self.bitrate_mode = Tkinter.StringVar(brf)
        self.bitrate_mode.set('constant')
        
        bc = Tkinter.Radiobutton(brf,
                                 text = 'Constant bit rate (Kbits/s)',
                                 variable = self.bitrate_mode,
                                 value = 'constant')
        bc.grid(row = 0, column = 0, sticky = 'w')
        self.bit_rate = Tkinter.IntVar(brf)
        self.bit_rate.set(default_bit_rate)
        er = Tkinter.Entry(brf, width=4, textvariable = self.bit_rate)
        er.grid(row = 0, column = 1, sticky = 'w')
        lc = Tkinter.Label(brf, text = ' (low 200, medium 1000, high 6000)')
        lc.grid(row = 0, column = 2, sticky = 'w')
        
        qf = Tkinter.Frame(mof)
        qf.grid(row=2,column=0,sticky='w')
        bv = Tkinter.Radiobutton(qf,
                                 text = 'Variable bit rate. Q (1-31)',
                                 variable = self.bitrate_mode,
                                 value = 'variable')
        bv.grid(row = 0, column = 0, sticky = 'w')
        self.qscale = Tkinter.IntVar(qf)
        self.qscale.set(5)
        eq = Tkinter.Entry(qf, width=2, textvariable = self.qscale)
        eq.grid(row = 0, column = 1, sticky = 'w')
        lq = Tkinter.Label(qf, text = ' (low 20, medium 10, high 1)')
        lq.grid(row = 0, column = 2, sticky = 'w')

        ## -----------------------------------------------------

        class FrRateTkOption(tkoptions.SymbolicEnumOption):
            labels=["24", "25", "30","50", "60"]
            values=["24", "25", "30","50", "60"]


        self.frRateEnumFrame  = Tkinter.Frame(self.movOptionsFrame)
        self.frRateEnumOption = FrRateTkOption(self.frRateEnumFrame,
                                               0, 'Frames per second',
                                               '25', self.updateFpsCB) 
        
        self.frRateEntryFrame  = Tkinter.Frame(self.movOptionsFrame)
        self.frRateEntryOption = tkoptions.StringOption(self.frRateEntryFrame,
                                                        0, 'Frames per second',
                                                        '25', self.updateFpsCB,
                                                        width = 3) 

        self.frRateEntryFrame.grid(row=2, column=0, sticky='w')
        self.useFrOption = self.frRateEntryOption
        
        ## --------------------------------------------------------
        bsf = Tkinter.Frame(self.movOptionsFrame)
        bsf.grid(row=3,column=0,sticky='w')

        self.buffer_size = Tkinter.IntVar(bsf)
        self.buffer_size.set(default_buffer_size)
        bsl = Tkinter.Label(bsf, text = 'Buffer size (Kbytes)')
        bsl.grid(row = 0, column = 0, sticky = 'w')
        eb = Tkinter.Entry(bsf, width=4, textvariable = self.buffer_size)
        eb.grid(row = 0, column = 1, sticky = 'w')
        
        ## --------------------------------------------------------
        self.bounceVar = Tkinter.IntVar(self.movOptionsFrame)
        bnc  = Tkinter.Checkbutton(self.movOptionsFrame,
                                   variable=self.bounceVar,
                                   text="Play forward then backward")
        bnc.grid(row=4, column=0, sticky='w')
        
        ## --------------------------------------------------------
        sff = Tkinter.Frame(self.movOptionsFrame)
        sff.grid(row=5, column=0, sticky='w')

        fh = Tkinter.Label(sff, text = 'Set standard format: ')
        fh.grid(row = 0, column = 0, sticky = 'w')

        b1 = Tkinter.Button(sff, text = VCD,
                            command = lambda: self.standard_format(VCD))
        b1.grid(row = 0, column = 1, sticky = 'w')
        b2 = Tkinter.Button(sff, text = SVCD,
                            command = lambda: self.standard_format(SVCD))
        b2.grid(row = 0, column = 2, sticky = 'w')

        b3 = Tkinter.Button(sff, text = DVD,
                            command = lambda: self.standard_format(DVD))
        b3.grid(row = 0, column = 3, sticky = 'w')

    def synchDirector(self,director):
        self.director = director

        if director.hasState():	  
            self.disableInputOptions() 
            self._notifyGfxSize("%sx%s" % tuple(director.getGfxWindowSize()))
            self._notifyFrameCount(director.getFrameCount())
            self._notifyMovieTime(director.getFrameCount()/25)
            
            if director.isRecording():	 
                self._notifyRecordingStart()	 
            else:	 
                self._notifyRecordingStop()	 
            if director.isEncoding():	 
                self._notifyEncodingStart()	 
        #else:	 
        #    mr._notifyRecorderReset()


    def updateFpsCB(self, event):
        fps = event.get()

        try:
            n = string.atoi(fps)
        except ValueError:
            pass
        else:
            if self.director:
                self.director.setFps(n)

    def chooseFmtCB(self, event=None):

        new_fmt = self.movieFmtOption.get()

        self.replaceExt(new_fmt)

        if new_fmt[limited_frame_rate_field]:
            self.showFrmRateEnum()      # limited frame rates
        else:
            self.showFrmRateEntry()
            
            
    def showFrmRateEntry(self):
        try:
            self.frRateEnumFrame.grid_forget()
        except:
            pass

        self.frRateEntryFrame.grid(row=2, column=0, sticky='w')
        self.useFrOption = self.frRateEntryOption
        self.updateFpsCB(self.frRateEntryOption)

    def showFrmRateEnum(self):
        try:
            self.frRateEntryFrame.grid_forget()
        except:
            pass
        
        self.frRateEnumFrame.grid(row=2, column=0, sticky='w')
        self.useFrOption = self.frRateEnumOption
        self.updateFpsCB(self.frRateEnumOption)
        
    def replaceExt(self, new_fmt):
        out_file = self.outFileOption.get()
        base, ext = os.path.splitext(out_file)
        self.outFileOption.set(base + '.' + new_fmt[file_suffix_field])

    def standard_format(self, preset_name):

        settings = standard_formats[preset_name]
        self.bitrate_mode.set('constant')
        self.bit_rate.set(settings['bit_rate'])
        self.buffer_size.set(settings['buf_size'])
        self.director.setGfxWindowSize(*settings['resolution'])
        self.movieFmtOption.set(settings['format'])
        self.chooseFmtCB()      # Setting variable does not invoke callback.

    def raytraceCB(self):
        if self.raytraceVar.get():
            fmts = raytraceImageFormats
            defaultFmt = defaultRaytraceImageFormat
        else:
            fmts = imageFormats
            defaultFmt = defaultImageFormat
        io = self.imgFmtOption
        io.labels=['%s [.%s]' % (f, f.lower()) for f in fmts]
        io.values=fmts
        io.remakeMenu()
        if not io.get() in io.values:
            io.set(defaultFmt)

    def raytraceOptionsCB(self):
        from chimera.dialogs import display
        d = display("preferences")
        from chimera.printer import POVRAY_SETUP
        d.setCategoryMenu(POVRAY_SETUP)

    def resetModeCB(self):
        if self.autoResetVar.get():
            if self.keepSrcVar.get():
                mode = RESET_KEEP
            else:
                mode = RESET_CLEAR
        else:
            mode = RESET_NONE
                
        self.director.setResetMode(mode)

    def getCurrentDimensions(self):
        ## get the size...
        geom = self._toplevel.wm_geometry()
        #print "GEOM IS ", geom
        dimensions = geom.split('+',1)[0].split('-',1)[0]
        width, height = dimensions.split('x')
        return int(width),int(height)

    def doCustomResize(self, evt=None):
        width  = int(self.custResWidthE.get())
        height = int(self.custResHeightE.get())

        new_width  = self.director.findNextMacroblock(width)
        new_height = self.director.findNextMacroblock(height)

        self.director.setGfxWindowSize(new_width, new_height)

        self.custResWidthE.delete(0,'end')
        self.custResWidthE.insert(0,new_width)

        self.custResHeightE.delete(0,'end')
        self.custResHeightE.insert(0,new_height)

        
    def getTargetSize(self):
        if self.frmOptionsVar.get():
            if self.movOptionsVar.get():
                return self.both_width, self.both_height
            else:
                return self.frm_width, self.frm_height
        elif self.movOptionsVar.get():
            return self.mov_width, self.mov_height
        else:
            return self.cache_width, self.cache_height

    def showFrmOptionsCB(self):
        self.showOptionsCB('frame')
        
    def showMovOptionsCB(self):
        self.showOptionsCB('movie')

    def showOptionsCB(self, option):

        if option == 'frame':
            VAR   = self.frmOptionsVar
            FRAME = self.frmOptionsFrame
            ROW   = FRM_OPTS_ROW
            HEIGHT= self.frm_height
        elif option == 'movie':
            VAR   = self.movOptionsVar
            FRAME = self.movOptionsFrame
            ROW   = MOV_OPTS_ROW
            HEIGHT= self.mov_height

        current_w,current_h = self.getCurrentDimensions()

        if VAR.get():
            FRAME.grid(row=ROW, column=0, columnspan=3, sticky='nsew')

            self._toplevel.wm_geometry(newGeometry='%sx%s' % (current_w, current_h + HEIGHT))

        else:
            FRAME.grid_forget()
            self._toplevel.wm_geometry(newGeometry='%sx%s' % (current_w, current_h - HEIGHT))
                
    ## Button callbacks


    ## The callback for start recording happens in two parts:
    ## (1) Code that actually tells the director to start recording, and
    ## (2) Code that updates the GUI so it looks like it's recording
    ## These are put in seperate functions so they can be called
    ## seperately
    
    def startRecording(self):

        patt = self.inputPatternOption.get()
        input_pattern = ''
        if patt:
            input_pattern = patt
        else:
            input_pattern = DEFAULT_PATTERN % getRandomChars()
            self.inputPatternOption.set(input_pattern)
        
        img_fmt = self.imgFmtOption.get()
        img_dir = self.inputDirOption.get() or tempfile.gettempdir()
        if self.useSuperSampleVar.get():
            supersample = self.superSampleOption.get()
        else:
            supersample = 0
        raytrace = self.raytraceVar.get()

        try:
            self.director.startRecording(img_fmt, img_dir, input_pattern,
                                         supersample, raytrace)
        except MovieError, what:
            self.showStatus("%s" % what, color="red")
        #else:
        #    self.startRecordingGUIConfig()

    #def startRecordingGUIConfig(self):
    def _notifyRecordingStart(self):
        ## <-------code that updates the gui--------->
        # 
        self.actionLabel.configure(text="Recording", fg='red')

        ## set button states to disabled
        #self.recButton.configure(image=self.pause_img, command=self.stopRecording)
        self.recButton.configure(text="Stop", state='normal', command=self.stopRecording)
        help.register(self.recButton,   balloon="Stop capturing frames from graphics window")

        self.clearButton.configure(state='disabled')
        self.encButton.configure(state='disabled')

        self.disableInputOptions()

    def disableInputOptions(self):
        """helper function to disable all input-file (i.e. frame-related)
        input options"""

        ## only do this once - once they start recording anything
        ## they can't switch up the format. the encoder will *not*
        ## appreciate this.
        self.imgFmtOption.disable()
        self.superSampleOption.disable()
        self.superSampleButton.configure(state = 'disabled')
        self.raytraceButton.configure(state = 'disabled')
        #self.movieSizeOption.disable() 
        self.inputDirOption.disable()
        self.inputPatternOption.disable()
        
    def enableInputOptions(self):
        """helper function to enable all input-file (i.e. frame-related)
        input options"""
        
        ## the user is now free to choose another input format
        ## and/or input directory            
        self.inputDirOption.enable()
        self.inputPatternOption.enable()
        self.imgFmtOption.enable()
        self.superSampleOption.enable()
        self.superSampleButton.configure(state = 'normal')
        self.raytraceButton.configure(state = 'normal')
        #self.movieSizeOption.enable()

    def stopRecording(self):
        if not self.director.isRecording():
            self.showStatus("Not currently recording")
            return
        
        try:
            self.director.stopRecording()
        except MovieError, what:
            self.showStatus("%s" % what, color="red")
        #else:
        #    self.stopRecordingGUIConfig()
                

    def _notifyRecordingStop(self):
        self.showStatus("Stopped recording", blankAfter=20)
        self.actionLabel.configure(text="Stopped", fg='black')

        ## restore button states to normal
        #self.recButton.configure(image=self.rec_img, command=self.startRecording)
        self.recButton.configure(text="Record", state='normal', command=self.startRecording)
        help.register(self.recButton,   balloon="Start capturing frames from the graphics window")

        self.encButton.configure(state='normal')
        self.clearButton.configure(state='normal')
        

    def _notifyRecorderReset(self):
        """this is called from outside the module, probably by the
        directory, to notify me (the gui) that the recorder
        has been reset"""

        self.accum_frames_var.set('0')
        self.accum_secs_var.set('0s.')
        self.clearButton.configure(state='disabled')

        self.enableInputOptions()

        if self.keepSrcVar.get():
            ## if you kept the last set of input images
            if self.inputPatternOption.get()[0:9]=='chimovie_':
                ## and didn't change (presumably) the input pattern
                self.inputPatternOption.set(DEFAULT_PATTERN % getRandomChars())
            ## else, we won't touch your 'custom' pattern

        self.encButton.configure(text="Make movie", state='disabled',
                                 command=self.startEncoding)

        self.recButton.configure(text="Record", state='normal',
                                 command=self.startRecording)

        self.actionLabel.configure(text="Stopped", fg='black')
        
    def resetRecording(self):
                
        if not self.keepSrcVar.get():
            clr=True
        else:
            clr=False
            
        try:
            self.director.resetRecorder(clearFrames=clr)
        except MovieError, what:
            self.showStatus("%s" % what, color="red")


    def getFnamePattern(self, pattern, format):
        """ helper function - converts
        chimera-img-%d
        """
        pass

    def startEncoding(self):
        
        ## Encoder API -
        # 
        #   In order to encode a movie, the encoder will need to know
        #   some basic parameters, which will be passed to it in a dictionary
        #   with the following key/value pairs:
        #
        #   OUT_FILE       where to write the movie output
        #   INPUT_FORMAT   the format the individual frames are in
        #   INPUT_DIR      the directory where all the individual frames are saved
        #   INPUT_PATTERN  the pattern  of the input frame filenames
        #   INPUT_LAST     the last frame number to encode (assume 0 is the first)


        ## need to figure out what the user wants to do parameter-wise

        param_dict = {'OUT_FILE':      self.outFileOption.get(),
                      'FPS'    :       self.useFrOption.get()
                      }

        format = self.movieFmtOption.get()
        param_dict['FORMAT'] = format[file_format_field]
        if format[video_codec_field]:
            param_dict['VIDEO_CODEC'] = format[video_codec_field]
            
        if self.bitrate_mode.get() == 'constant':
            param_dict['BIT_RATE'] = self.bit_rate.get()
            param_dict['BUF_SIZE'] = self.buffer_size.get()
        else:
            param_dict['Q_SCALE'] = self.qscale.get()

        param_dict['PLAY_FORWARD_AND_BACKWARD'] = self.bounceVar.get()
        
        try:
            self.director.startEncoding(self.updateEncStatus, **param_dict)
        except MovieError, what:
            self.showStatus("%s" % what, color="red")
        
    def _notifyEncodingStart(self):
        self.statusLine.configure(textvariable=self.frame_num_var)
        self.actionLabel.configure(text="Encoding", fg='red')
        #self.encButton.configure(image=self.abort_img, command=self.abortEncoding)
        self.encButton.configure(text="Cancel movie", command=self.abortEncoding)
        help.register(self.encButton,   balloon="Cancel encoding of movie")

        ## establish constraints
        self.clearButton.configure(state='disabled')
        self.recButton.configure(state='disabled')

    def updateEncStatus(self, msg):
        self.frame_num_var.set(msg)

    def _notifyEncodingComplete(self, exit_status):
        """this is called from outside of this module, probably
        from the director, to notify me (the gui) that encoding
        has completed"""
        
        #self.actionLabel.configure(text="Stopped", fg='black')
        self.statusLine.configure(textvariable='')

        #self.encButton.configure(image=self.movie_img)
        self.encButton.configure(text="Make movie")
        help.register(self.encButton,   balloon="Make a movie from currently captured frames")

        ## re-enable buttons
        self.clearButton.configure(state='normal')
        self.recButton.configure(state='normal')
        self.encButton.configure(command=self.startEncoding)

        if exit_status == EXIT_SUCCESS:
            self.actionLabel.configure(text="Successfully encoded!!", fg='red')
                
        elif  exit_status == EXIT_CANCEL:
            self.actionLabel.configure(text="Canceled encoding!!", fg='red')

        elif exit_status == EXIT_ERROR:
            self.actionLabel.configure(text="Encoding error", fg='red')


    def abortEncoding(self):
        try:
            self.director.stopEncoding()
        except MovieError, what:
            self.showStatus("%s" % what, color="red")
            return
            
        self.showStatus("Attempt to cancel encoding....")

    def _notifyFrameCount(self, count):
        """this is called from outside of this module
        to notify me (the gui) that i should update any views
        of how many frames have been recorded"""
        
        self.accum_frames_var.set(count)

    def _notifyMovieTime(self, t):
        """this is called from outside of this module
        to notify me (the gui) to update any views of
        the estimated movie time"""

        self.accum_secs_var.set(t)

    def _notifyStatus(self, msg):
        """this is called from outside this module
        to notify me (the gui) to show some status
        string"""
        
        self.showStatus(msg)

    def _notifyError(self, err):
        """this is called from outside this module
        to notify me (the gui) to show some error
        string"""
        
        chimera.replyobj.error(err)
        self.showStatus(err, color='red')


    def _notifyInfo(self, info):
        """this is called from outside this module
        to notify me (the gui) to show some info
        string"""

        chimera.replyobj.info(info)
    
    def _notifyGfxSize(self, size):
        """this is called from outside this module
        to notify me (the gui) that the graphics window
        size has changed"""
        self.frame_res_var.set(size)

    def showStatus(self, msg, **kw):
        self.status(msg, **kw)
        
chimera.dialogs.register(MovieRecorderGUI.name, MovieRecorderGUI) 
