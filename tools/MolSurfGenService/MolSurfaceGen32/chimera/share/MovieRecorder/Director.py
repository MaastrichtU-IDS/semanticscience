from MovieRecorder import RESET_CLEAR, RESET_KEEP, RESET_NONE
from MovieRecorder import EXIT_ERROR, EXIT_CANCEL, EXIT_SUCCESS
from MovieRecorder import getTruncPath, MovieError

import chimera

import string, os

class UIReflector:
    def __init__(self):
        self.UIs = []

    def registerUI(self, ui):
        self.UIs.append(ui)

    def deregisterUI(self, ui):
        try:
            idx = self.UIs.index(ui)
        except ValueError:
            pass
        else:
            del self.UIs[idx]

    def _notifyStatus(self, status):
        [ui._notifyStatus(status) for ui in self.UIs]

    def _notifyError(self,error):
        #[ui._notifyError(error) for ui in self.UIs]
        if not len(self.UIs) == 0:
            self.UIs[0]._notifyError(error)

    def _notifyInfo(self,info):
        #[ui._notifyInfo(info) for ui in self.UIs]
        if not len(self.UIs) == 0:
            self.UIs[0]._notifyInfo(info)

    def _notifyEncodingComplete(self,exit_status):
        [ui._notifyEncodingComplete(exit_status) for ui in self.UIs]
    def _notifyRecorderReset(self):
        [ui._notifyRecorderReset() for ui in self.UIs]

    def _notifyFrameCount(self,count):
        [ui._notifyFrameCount(count) for ui in self.UIs]
    def _notifyMovieTime(self,mtime):
        [ui._notifyMovieTime(mtime) for ui in self.UIs]
    def _notifyGfxSize(self,newsize):
        [ui._notifyGfxSize(newsize) for ui in self.UIs]

    def _notifyRecordingStart(self):
        [ui._notifyRecordingStart() for ui in self.UIs]
    def _notifyRecordingStop(self):
        [ui._notifyRecordingStop() for ui in self.UIs]
    def _notifyEncodingStart(self):
        [ui._notifyEncodingStart() for ui in self.UIs]
    


class Director:
    """ Because it's a movie, and the director coordinates everything."""
    
    def __init__(self):
        self.ui = UIReflector()
        self.recorder = None
        self.encoder  = None

        self.resetMode = RESET_CLEAR
        self.lastSize = (None, None)

        top = chimera.tkgui.app.winfo_toplevel()
        top.bind('<Configure>', self.updateGfxSize)

        self.fps = 25

    def registerUI(self, ui):
        self.ui.registerUI(ui)
    
    def setResetMode(self, mode):
        self.resetMode = mode

    def isRecording(self):
        if not self.recorder:
            return False
        else:
            return self.recorder.isRecording()

    def isEncoding(self):
        return self.encoder != None

    def hasState(self):
        ## Return True if the Director 'has state', that is,
        ## is in the middle of recording a movie already.
        ## Else return False
        if not self.recorder:
            return False
        else:
            return self.recorder.getFrameCount() != 0

    def getFrameCount(self):
        ## return the recorder's frame count
        if self.recorder:
            return self.recorder.getFrameCount()
        else:
            return 0

    def getRecInputPattern(self):
        return self.recorder.getInputPattern()

    def getRecImgDir(self):
        return self.recorder.getImgDir()

    def getRecImgFmt(self):
        return self.recorder.getImgFormat()

    #def clearFrames(self):
    #    if self.recorder:
    #        self.recorder.clearFrames()

    def _informStatus(self, status):
        """lower level components (recorder and encoder) call this to
        inform me of some status that needs to be propagated up to the gui
        """
        self.ui._notifyStatus(status)

    def _informError(self, error):
        """lower level components (recorder and encoder) call this to
        inform me of some error that needs to be propagated up to the gui
        """
        self.ui._notifyError(error)

    def _informInfo(self, info):
        """lower level components (recorder and encoder) call this to
        inform me of some info that needs to be propagated up to the gui
        """
        self.ui._notifyInfo(info)

    def _informEncodingDone(self, exit_val, exit_status, error_msg):
        """ the encoder calls this to notify me that it has finished
        encoding. arguments convey the exit status of the encoding
        process"""

        ## let the ui do whatever else it has to to right its state
        self.ui._notifyEncodingComplete(exit_status)

        path = getTruncPath(self.encoder.getOutFile())
        
        self.encoder = None

        ## You only want to do any kind of reset if the encoder ran
        ## successfully. Don't reset state if encoding was canceled
        ## or there was an error (user may want to change parameters
        ## and re-encode). Also, if resetMode is 'none', you don't want
        ## to do any kind of reset.
        if (exit_status==EXIT_SUCCESS and self.resetMode!=RESET_NONE):
            clr = [False,True][self.resetMode==RESET_CLEAR]
            self.resetRecorder(clearFrames=clr)
        
        if exit_status == EXIT_SUCCESS:
            success_msg = "Movie saved to %s" % path
            self.ui._notifyStatus(success_msg)
            self.ui._notifyInfo(success_msg + '\n')

        elif  exit_status == EXIT_CANCEL:
            self.ui._notifyStatus("Movie encoding has been canceled.")
            self.ui._notifyInfo("Movie encoding has been canceled.\n")
            
        elif exit_status == EXIT_ERROR:
            self.ui._notifyError("An error occurred during encoding. See Reply Log for details.")
            self.ui._notifyInfo("\nError during MPEG encoding:\n" 
                                "-----------------------------\n"
                                "Exit value:    %s\n"
                                "Error message: \n"
                                "%s\n"
                                "-----------------------------\n" %
                                (exit_val, error_msg)
                                )

    def _informFrameCount(self, count):
        """this method is called by the recorder to inform me of the
        number of frames that have been recorded"""
        
        self.ui._notifyFrameCount(count)
        self.ui._notifyMovieTime("%ss." % (count/self.fps))

    def startRecording(self, fformat, directory, pattern, supersample=0,
                       raytrace=False):
        r = self.recorder
        if r and r.isRecording():
            raise MovieError, "Already recording"
        if r:
            r.supersample = supersample
            r.raytrace = raytrace
        else:
            import RecorderHandler
            from RecorderHandler import RecorderError
            
            try:
                self.recorder = RecorderHandler.RecorderHandler(self, fformat, directory, pattern, supersample, raytrace)
            except RecorderError, what:
                raise MovieError, what

        self.recorder.start()
        self.ui._notifyRecordingStart()
        
    def stopRecording(self):
        if not self.recorder or (not self.recorder.isRecording()):
            raise MovieError, "Not currently recording"
        
        self.recorder.stop()
        self.ui._notifyRecordingStop()

    def startEncoding(self, updateFn, **kwargs):
        if self.encoder:
            raise MovieError, "Currently encoding a movie"

        if not self.recorder:
            raise MovieError, "No frames to encode"

        from MovieRecorder import checkLicense
        if not checkLicense():
            raise MovieError, "Must accept license agreement before using movie encoder" 

        basepat = self.recorder.getInputPattern().replace('*', '%05d')
        suffix = ".%s" % self.recorder.getImgFormat().lower()
        pattern = basepat + suffix

        import ffmpeg_encoder
        self.encoder = ffmpeg_encoder.EncoderHandler(self, updateFn,
                        FRAME_FORMAT  =   self.recorder.getImgFormat(),
                        FRAME_DIR     =   self.recorder.getImgDir(),
                        FRAME_PATTERN =   pattern, 
                        FRAME_LAST    =   self.recorder.getFrameCount(),
                        **kwargs)                                                     
        self.encoder.start()
        self.ui._notifyEncodingStart()

    def stopEncoding(self):
        if not self.encoder:
            raise MovieError, "Not currently encoding"

        self.encoder.abortEncoding()


    def setFps(self, fps):
        """called by a ui to set the frames per second"""
        self.fps = fps
        

    def resetRecorder(self, clearFrames=True):
        ## when recorder gui calls this, this should tell recordergui what to say
        ## instead of it figureing it out...
        ## so it can also tell command line what to say....

        if self.isEncoding():
            raise chimera.UserError, "Attempted movie reset when encoding not finished."

        if not self.recorder:
            raise MovieError, "No frames have been recorded"

        if self.recorder and self.recorder.isRecording():
            self.stopRecording()

        msg = ' - frames have been '
        if clearFrames:
            self.recorder.clearFrames()
            msg += "cleared"
        else:
            msg += "saved (%s.%s)" % (os.path.join(self.recorder.getImgDir(),
                                                self.recorder.getInputPattern()
                                                ),
                                      self.recorder.getImgFormat()
                                      )

        del self.recorder
        self.recorder = None

        self.ui._notifyStatus("Recorder has been reset %s" % msg)
        self.ui._notifyRecorderReset()


    def findNextMacroblock(self, val):
        val = int(val)
        
        if (val%16) == 0:
            return val
        else:
            return ( 16 * int(val/16) + 16 ) 
        

    def updateGfxSize(self, evt=None):
        """this is the callback when the user resizes the chimera
        graphics window. it basically does a call to update the gui,
        in case it cares to know about this change"""

        width, height = self.getGfxWindowSize()
        if (width, height) != self.lastSize:
            self.lastSize = (width, height)
            self.ui._notifyGfxSize('%sx%s' % (width, height))

    def setGfxWindowSize(self, width, height):
        """the helper function that actually does the work of
        resizing the Chimera graphics window"""

        ## don't need to do anything if current width and height
        ## is equal to requested width and height
        cur_width, cur_height = self.getGfxWindowSize()
        if cur_width==width and cur_height==height:
            return

        chimera.viewer.windowSize = (width, height)
        chimera.tkgui.app.winfo_toplevel().geometry('')

    def getGfxWindowSize(self):
          return chimera.viewer.windowSize
    

    def dumpStatusInfo(self):
        import chimera

        if not self.recorder:
            ## not really an error, just that by using this call
            ## output will go to the reply log !
            self._informStatus("No frames have been recorded\n")
        else:
            self._informStatus("Status information written to Reply Log")
            self._informInfo(self.recorder.getStatusInfo())
