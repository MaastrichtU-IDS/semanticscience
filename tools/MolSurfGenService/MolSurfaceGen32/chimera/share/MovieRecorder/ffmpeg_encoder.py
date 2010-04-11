import threading, os, string
import chimera

from MovieRecorder import getTruncPath

from subprocess import *

ffmpeg_cmd = 'ffmpeg'

from MovieRecorder import EXIT_SUCCESS, EXIT_ERROR, EXIT_CANCEL, DEFAULT_OUTFILE

class EncoderHandler:

    def __init__(self, director, updateFn, **kwargs):
        self.director = director
        self.encoder = ffmpeg_encoder(updateFn, **kwargs)
        self.thread = None

    def getOutFile(self):
        return self.encoder.getOutFile()

    def start(self):
        from chimera.tkgui import runThread
        self.thread = runThread(self.encoder.run)
        chimera.tkgui.app.after(1000, self.checkEncodingDone)

    def abortEncoding(self):
        self.encoder.abortEncoding()

    def checkEncodingDone(self):
        if self.thread.isAlive():
            chimera.tkgui.app.after(1000, self.checkEncodingDone)
        else:
            exit_val, exit_status, error_msg = self.encoder.getExitStatus()
            
            if exit_status == EXIT_CANCEL or exit_status == EXIT_ERROR:
                self.encoder.deleteMovie()

            self.director._informEncodingDone(exit_val, exit_status, error_msg)


class ffmpeg_encoder:

    def __init__(self, updateFn, **param_dict):

        self.this_dir = os.path.split(os.path.abspath(__file__))[0]

        self.out_file   = param_dict['OUT_FILE']
        if not self.out_file:
            self.out_file = os.path.abspath(DEFAULT_OUTFILE)
            param_dict['OUT_FILE'] = self.out_file

        self.arg_list = self._buildArgList(param_dict)

        if param_dict['PLAY_FORWARD_AND_BACKWARD']:
            self.copy_frames_backwards(param_dict)

        self.encodeAbortEvt = threading.Event()
        self.updateFn = updateFn

        self.exit_status = (None, None, None)

        self.frame_num = -1
        self.time_rem  = -1

    def _buildArgList(self, param_dict):
        arg_list = []

        ## figure out rate parameter. if we were supplied with
        ## a framerate, stringify it. else, use the default of '25'.
        ##
        ## Frame rate command-line option must appear before input files
        ## command-line option because the rate describes the input sequence.
        ## Putting the -r after the input files has the undesired effect of
        ## eliminating frames at rates lower than 25 fps to keep the duration
        ## equal to the 25 fps input sequence duration.
        ##
        arg_list.append('-r')
        frt = param_dict['FPS']
        if frt:
            arg_list.append(str(frt))
        else:
            arg_list.append('25')

        arg_list.append('-i')
        arg_list.append (os.path.join(param_dict['FRAME_DIR'],
                                      param_dict['FRAME_PATTERN']) )

        ## so ffmpeg will overwrite the output file if it exists
        arg_list.append('-y')

        for param, option in (('VIDEO_CODEC', '-vcodec'),
                              ('FORMAT', '-f'),
                              ('RESOLUTION', '-s'),
                              ('BIT_RATE', '-b'),
                              ('BUF_SIZE', '-bufsize'),
                              ('Q_SCALE', '-qscale')):
            if param in param_dict:
                p = param_dict[param]
                if p:
                    arg_list.append(option)
                    arg_list.append(str(p))

        from OpenSave import tildeExpand
        path = tildeExpand(param_dict['OUT_FILE'])
        from os.path import dirname, isdir
        d =  dirname(path)
        if d and not isdir(d):
            from MovieRecorder import MovieError
            raise MovieError, 'Output directory does not exist: %s' % d
        arg_list.append(path)

        from CGLutil.findExecutable import findExecutable
        ffmpeg_exe = findExecutable(ffmpeg_cmd)
        if ffmpeg_exe:
            print '%s %s' % (ffmpeg_exe, ' '.join(arg_list))
        else:
            print 'ffmpeg arguments: %s' % ' '.join(arg_list)
        return arg_list

    def copy_frames_backwards(self, param_dict):

        pat = os.path.join(param_dict['FRAME_DIR'], param_dict['FRAME_PATTERN'])
        n = param_dict['FRAME_LAST'] + 1
        self.loop = (pat, n)
        if hasattr(os, 'link'):
            copy = os.link
        else:
            from shutil import copyfile
            copy = copyfile      # Cannot link on Windows XP
        for f in range(n):
            copy(pat % (n-1-f), pat % (n+f))
            
    def remove_backwards_frames(self):

        if hasattr(self, 'loop'):
            pat, n = self.loop
            for f in range(n):
                os.remove(pat % (n+f))
            
    def _parseOutput(self, out_line):
        ## frame=   36 q=2.0 Lsize=      28kB time=1.4 bitrate= 163.8kbits/s
        if out_line[0:6] == "frame=":
            return out_line
        else:
            return None

    def parseOutput(self, out_line):
        #ESTIMATED TIME OF COMPLETION:  0 seconds
        #FRAME 35 (B):  I BLOCKS:  0;  B BLOCKS:  685   SKIPPED:  251 (0 seconds)

        if out_line.find('ESTIMATED TIME OF COMPLETION') >= 0:
            time_info = out_line.split(':',1)[1].strip()
            amt, units = time_info.split()
            if units.strip() == 'minutes':
                return {'time': '%s min.' % amt}
            else:
                return {'time': '%s sec.' % self.convertToMinSecs(amt)}

        elif out_line[0:5] == 'FRAME':
            frame_info = out_line.split(':',1)[0]
            frame_num = frame_info.split()[1]
            return {'frame':frame_num}
        else:
            return None

    def getOutFile(self):
        return self.out_file

    def abortEncoding(self):
        self.encodeAbortEvt.set()

    def deleteMovie(self):
        try:
            os.remove(self.out_file)
        except:
            pass

    def killEncoder(self, pop_obj):
	try:
		pop_obj.stdin.write('q')
		pop_obj.stdin.flush()
	except IOError:
		pass


    def convertToMinSecs(self, secs):
        secs = int(secs)

        if secs < 60:
            return "%s" % secs
        else:
            return "%d:%02d" % (secs/60, secs%60)


    def getExitStatus(self):
        return self.exit_status


    def run(self, message_queue):

        from CGLutil.findExecutable import findExecutable
        ffmpeg_exe = findExecutable(ffmpeg_cmd)
        if ffmpeg_exe is None:
            self.exit_status = (-1, EXIT_ERROR,
                                 'Could not find %s executable' % ffmpeg_cmd)
            return

	# all output is on stderr, but Windows needs all standard I/O to
	# be redirected if one is, so stdout is a pipe too
        pop_obj = Popen([ffmpeg_exe] + self.arg_list,
                        stdin=PIPE, stdout=PIPE, stderr=STDOUT)

        pid = pop_obj.pid

        killed = False
        while pop_obj.poll() == None:

            if self.encodeAbortEvt.isSet():
                self.killEncoder(pop_obj)
                killed = True
                #print "gonna kill ", pid

            if killed:
                continue

            output_line = pop_obj.stdout.readline()
            if not output_line:
                continue

            output = self._parseOutput(output_line)
            if not output:
                continue

            # Status reports use queue to execute in main thread
            # since Tk calls made from threads cause crashes.
            report_status = lambda s=self, o=output: s.updateFn(o)
            message_queue.put(report_status)

        exit_val = pop_obj.returncode

        status = None
        error  = None

        if exit_val == 0:
            if not killed:
                status = EXIT_SUCCESS
            else:
                status = EXIT_CANCEL
        else:
            status = EXIT_ERROR
            error_lines = pop_obj.stdout.readlines()
            if len(error_lines) < 10:
                error = string.join(error_lines)
            else:
                error = string.join(error_lines[-10])

        self.exit_status = (exit_val, status, error)

        self.remove_backwards_frames()
