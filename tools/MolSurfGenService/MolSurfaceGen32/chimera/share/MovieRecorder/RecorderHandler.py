import chimera

import glob, os

from MovieRecorder import DEFAULT_PATTERN, getRandomChars

class RecorderError(Exception):
    pass

class RecorderHandler:

    def __init__(self, director, img_fmt=None, img_dir=None, input_pattern=None,
                 supersample=0, raytrace=False):

        if not img_fmt:
            self.img_fmt = "PNG"
        else:
            self.img_fmt = img_fmt.upper()

        if not img_dir:
            import tempfile
            self.img_dir = tempfile.gettempdir()
        else:
            self.img_dir = img_dir
            
        if not input_pattern:
            self.input_pattern = DEFAULT_PATTERN % getRandomChars()
        else:
            if not input_pattern.count("*")==1:
                raise RecorderError, "Image pattern must have one and only one '*'"
            self.input_pattern = input_pattern

        self.supersample = supersample
        self.raytrace = raytrace

        self.director = director

        self.newFrameHandle = None

        self.frame_count     = -1

        #self.chimera_winsize = (None,None)
        self.RECORDING = False
	self.task = None

    def start(self):        
        self.newFrameHandle = chimera.triggers.addHandler('post-frame', self.captureImage, None)
        self.RECORDING = True
	from chimera.tasks import Task
	self.task = Task("record movie", self.cancelCB)

    def cancelCB(self):
	# If user cancels inside of captureImage/saveImage, this callback
	# is never invoked because of the exception thrown in saveImage
	# happens before this function is called.  So we 
	self.director.stopRecording()
	self.director._informStatus("movie recording aborted by user")

    def stop(self):
        chimera.triggers.deleteHandler('post-frame', self.newFrameHandle)
        self.RECORDING = False
	self.task = None

    def reset(self):
        self.frame_count = -1
        self.img_dir = None
        self.img_fmt = None
        self.input_pattern = None
        
    def isRecording(self):
        return self.RECORDING

    def clearFrames(self):
        src_img_pattern = os.path.join(self.img_dir,
                                       self.input_pattern \
                                       + ".%s" % self.img_fmt.lower()
                                       )
        
        src_img_paths = glob.glob(src_img_pattern)

        for s in src_img_paths:
            try:
                os.remove(s)
            except:
                chimera.replyobj.error("Error removing file %s" % s)


    def getFrameCount(self):
        return self.frame_count

    def getInputPattern(self):
        return self.input_pattern

    def getImgFormat(self):
        return self.img_fmt

    def getImgDir(self):
        return self.img_dir

    def getStatusInfo(self):
        status_str  =  "-----Movie status------------------------------\n "
        status_str  += " %s\n" % (["Stopped","Recording"][self.isRecording()])
        status_str  += "  %s frames (in '%s' format) saved to directory '%s' using pattern '%s' .\n" % \
                       (self.getFrameCount(), self.getImgFormat(),self.getImgDir(), self.getInputPattern())
        status_str  += "  Est. movie length is %ss.\n" % (self.getFrameCount()/24)
        status_str  += "------------------------------------------------\n"
        return status_str
                

    def captureImage(self, trigger, closure, data):

        self.frame_count += 1
        self.director._informFrameCount(self.frame_count)
        if self.frame_count%10 == 0:
            self.director._informStatus("Capturing frame #%d " % self.frame_count)

        basename = self.input_pattern.replace('*','%05d') % self.frame_count
        suffix = '.%s' % self.img_fmt.lower()
        save_filename = basename + suffix
        save_path = os.path.join(self.img_dir, save_filename)

        from chimera.printer import saveImage
	from chimera import NonChimeraError
        try:
            saveImage(save_path,
                      format = self.img_fmt,
                      supersample = self.supersample,
                      raytrace = self.raytrace,
                      raytraceWait = True,
                      raytracePreview = False,
                      hideDialogs = False,
                      raiseWindow = False,
                      statusMessages = False,
		      task = self.task
                      )
        except NonChimeraError, s:
            # Raytracing aborted.
            self.director.stopRecording()
            self.director._informStatus(str(s))
            self.frame_count -= 1
            self.director._informFrameCount(self.frame_count)
        except:
            self.director.stopRecording()
            self.director._informStatus("Error capturing frame. Resetting recorder.")
            self.director.resetRecorder(clearFrames=True)
            raise
