## this is a package
import os, os.path, sys, string
import chimera
from chimera.baseDialog import ModalDialog

EXIT_ERROR   = "ERROR"
EXIT_CANCEL  = "CANCEL"
EXIT_SUCCESS  = "SUCCESS"


DEFAULT_PATTERN  = "chimovie_%s-*"
DEFAULT_OUTFILE = "chimera_movie.mov"


RESET_CLEAR = 'clear'
RESET_KEEP  = 'keep'
RESET_NONE  = 'none'

director = None


class AcceptLicenseDialog(ModalDialog):

    title   = "Accept MPEG License"
    buttons = ('Accept', 'Decline')
    provideStatus = False

    def fillInUI(self, parent):

        import Tkinter
        license_lbl = Tkinter.Label(parent, text="You must read and accept the following agreement before\n" \
                                    "using Chimera's \"Movie Recorder\" tool:",
                                    justify='left'
                                    )
        license_lbl.grid(row=0, column=0, sticky='w', pady=5)
        
        license_txt = \
                    "<font size=12><b> Legal Disclaimer - Proprietary Media Formats</b></font>" \
                    "<p>Two of the video formats (MPEG-2 and MPEG-4) supported by Chimera's " \
                    "\"Movie Recorder\" tool are encoded using proprietary algorithms which are " \
                    "protected by patents. The <a href='http://www.mpeg-la.com'>MPEG-LA</a> " \
                    "(licensing authority) is the organization responsible for collecting " \
                    "royalties on MPEG-related technologies.</p>" \
                    "<br>" \
                    "<p>Anyone who intends to use these technologies for commercial purposes " \
                    "is required by law to pay the appropriate fees to the licensing " \
                    "authority. While there has been no precedent of legal action taken " \
                    "against those who utilize these technologies for personal use, this can " \
                    "still be construed as a violation of the patent and may be subject to " \
                    "legal action. Chimera uses third party software called  " \
                    "<a href='http://ffmpeg.sourceforge.net'>FFmpeg</a> to handle video encoding. " \
                    "More information on legal issues associated with using this software can be found in the " \
                    "<a href='http://ffmpeg.sourceforge.net/legal.php'>Frequently Asked Questions</a> " \
                    "section of their Web site.</p> " \
                    "<br>" \
                    "<p>By using the \"Movie Recorder\" tool, you assume full responsibility for " \
                    "any royalties that might be due as a result of utilizing this patented " \
                    "technology.</p>"
                              

        from chimera.HtmlText import HtmlText
        import Pmw
        
        self.infoText = Pmw.ScrolledText(parent,
                                         text_pyclass = HtmlText,
                                         text_relief = 'sunken',
                                         text_wrap   = 'word',
                                         text_width  = 50,
                                         text_height = 8
                                         )

        self.infoText.settext(license_txt)
        
        self.infoText.configure(text_state='disabled', hscrollmode='dynamic',
                                vscrollmode = 'dynamic',
                                text_background = parent.cget('background')
                                )
        self.infoText.grid(row=1,column=0,sticky='nsew', pady=5)
        parent.rowconfigure(1, weight=1)
        parent.columnconfigure(0, weight=1)

    def Accept(self):
        ModalDialog.Cancel(self, value=True)
    def Decline(self):
        ModalDialog.Cancel(self, value=False)


def checkLicense():
    from prefs import prefs, LICENSE_AGREE

    if not prefs[LICENSE_AGREE]:
        dlg = AcceptLicenseDialog()
        res = dlg.run(chimera.tkgui.app)
        if res:
            prefs[LICENSE_AGREE] = True
            return True
        else:
            prefs[LICENSE_AGREE] = False
            return False

    else:
        return True
        

def getTruncPath(path):
    path_elts = path.split(os.path.sep)

    ## becuase save path is absolute, the first elt will be ''
    if not path_elts[0]:
        path_elts = path_elts[1:]

    if len(path_elts) <= 4:
        return path
    else:
        first_two = os.path.join(*path_elts[0:2])
        #print "first_two is ", first_two
        last_two  = os.path.join(*path_elts[-2:])
        #print "last_two is ", last_two 

        return os.path.sep + os.path.join(first_two, "...", last_two)

    ## don't need the last 
    #path_elts = path_elts[:-1]


def getRandomChars():
    import string, random
    
    l = []
    for i in string.letters + string.digits:
        l.append(i)
    random.shuffle(l)

    return string.join(l[0:4],'')


class MovieError(Exception):
    pass

## ----------------- gui interface ----------------------

def showMRDialog():
    
    import chimera
    from RecorderGUI import MovieRecorderGUI 

    director = getDirector()

    mr_exists = chimera.dialogs.find(MovieRecorderGUI.name)
    mr        = chimera.dialogs.display(MovieRecorderGUI.name)

    if not mr_exists:
        mr.synchDirector(director)
        director.registerUI(mr)
        
    
## ------------------ command line interface -------------------

class BaseRecorderGUI:
    def __init__(self):
        pass
    def _notifyFrameCount(self, count):
        pass
    def _notifyMovieTime(self, t):
        pass
    def _notifyRecorderReset(self):
        pass
    def _notifyStatus(self, msg):
        pass
    def _notifyThreadStatus(self, msg):
        pass
    def _notifyError(self, err):
        pass
    def _notifyInfo(self, info):
        pass
    def _notifyEncodingComplete(self, exit_status):
        pass
    def _notifyGfxSize(self, size):
        pass
    def _notifyRecordingStart(self):
        pass
    def _notifyRecordingStop(self):
        pass
    def _notifyEncodingStart(self):
        pass

class CmdLineGUI(BaseRecorderGUI):

    def _notifyStatus(self, msg):
        chimera.replyobj.status(msg)
        
    def _notifyThreadStatus(self, msg):
        self._notifyStatus(msg)

    def _notifyError(self, err):
        chimera.replyobj.error(err)
        self._notifyStatus(err)

    def _notifyInfo(self, info):
        chimera.replyobj.info(info)
    
    def _notifyGfxSize(self, size):
        self. _notifyStatus("Chimera graphics window is now %s pixels" % size)


cmdLineUI = None

def processMovieCmd(action, directory=None, pattern=None, fformat=None,
                    output=None, bitrate=None, buffersize=None,
                    qscale=None, framerate=None, mformat=None,
                    preset=None, resetMode=RESET_CLEAR, supersample=0,
                    raytrace=False, roundtrip=False):
    
    from Midas import MidasError

    director = getDirector()

    global cmdLineUI
    if not cmdLineUI:
        cmdLineUI = CmdLineGUI()
        director.registerUI(cmdLineUI)
    
    if action == "record":

        import RecorderGUI
        if fformat is None:
            if raytrace:
                fformat = RecorderGUI.defaultRaytraceImageFormat
            else:
                fformat = RecorderGUI.defaultImageFormat
        else:
            if raytrace:
                fmts = RecorderGUI.raytraceImageFormats
            else:
                fmts = RecorderGUI.imageFormats
            fformat = fformat.upper()
            if not fformat in fmts:
                raise MidasError, 'Unsupported image file format %s, use %s' % (fformat, ', '.join(fmts))

        try:
            director.startRecording(fformat, directory, pattern,
                                    supersample, raytrace)
        except MovieError, what:
            raise MidasError, what
                
    elif action == "stop":
        try:
            director.stopRecording()
        except MovieError, what:
            raise MidasError, what

    elif action == "encode":

        r = director.recorder
        if r and r.isRecording():
            director.stopRecording()
            
        kw = {'OUT_FILE': output,
              'BIT_RATE': bitrate,
              'BUF_SIZE': buffersize,
              'Q_SCALE': qscale,
              'FPS': framerate,
              'PLAY_FORWARD_AND_BACKWARD': roundtrip}
            
        from RecorderGUI import command_formats, default_format, file_format_field, file_suffix_field, video_codec_field, standard_formats, default_bit_rate, default_buffer_size

        if bitrate == None and qscale == None:
            kw['BIT_RATE'] = default_bit_rate

        if buffersize == None:
            kw['BUF_SIZE'] = default_buffer_size

        if mformat == None:
            format = default_format
        elif mformat in command_formats:
            format = command_formats[mformat]
        else:
            raise MidasError, 'Unrecognized movie format %s' % mformat
        kw['FORMAT'] = format[file_format_field]
        kw['VIDEO_CODEC'] = format[video_codec_field]

        if preset:
            preset = preset.upper()
            if preset in standard_formats:
                settings = standard_formats[preset]
                kw['RESOLUTION'] = '%dx%d' % settings['resolution']
                format = settings['format']
                kw['FORMAT'] = format[file_format_field]
                kw['BIT_RATE'] = settings['bit_rate']
                kw['BUF_SIZE'] = settings['buf_size']
                del kw['Q_SCALE']
            else:
                raise MidasError, 'Unrecognized preset "%s" (%s)' % (preset, ', '.join(standard_formats.keys()))
            
        if output == None:
            file = os.path.abspath(DEFAULT_OUTFILE)
            file = os.path.splitext(file)[0] + '.' + format[file_suffix_field]
            kw['OUT_FILE'] = file

        try:
            director.setResetMode(resetMode)
            director.startEncoding(cmdLineUI._notifyThreadStatus, **kw)
        except MovieError, what:
            raise MidasError, what
        
    elif action == "abort":
        try:
            director.stopEncoding()
        except MovieError, what:
            raise MidasError, what

    elif action == "reset":

        if resetMode == RESET_CLEAR:
            clr = True
        else:
            clr = False
        
        try:
            director.resetRecorder(clearFrames=clr)
        except MovieError, what:
            raise MidasError, what
        
        
    elif action == "status":
        director.dumpStatusInfo()
        
    else:
        raise MidasError, "Unrecognized movie command '%s'" % action


def getDirector():
    global director    

    if director:
        return director
    else:
        import Director
        director = Director.Director()
        return director
