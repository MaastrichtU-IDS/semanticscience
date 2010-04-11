## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Console output.
"""
import sys

class ConesoleOutput(object):
    def __init__(self, stderr = sys.stderr):
        self.disabled = False
        self.stderr = stderr

    def warning(self, message):
        if self.disabled:
            return
        message = "[MMLIB:WARNING] %s\n" % (message)
        try:
            self.stderr.write(message)
        except IOError:
            pass
        
    def debug(self, message):
        return
        if self.disabled:
            return
        message = "[MMLIB:DEBUG] %s\n" % (message)
        try:
            self.stderr.write(message)
        except IOError:
            pass
        
    def fatal(self, message):
        if not self.disabled:
            message = "[MMLIB:DEBUG] %s\n" % (message)
            try:
                self.stderr.write(message)
            except IOError:
                pass
        raise SystemExit

console_output_object = ConesoleOutput()

def SetConsoleOutputObject(co):
    """Sets the console output to a new object.
    """
    global console_output_object
    console_output_object = co

def disable():
    """Disables console output.
    """
    console_output_object.disabled = True

def enable():
    """Enables console output.
    """
    console_output_object.disabled = False

def warning(message):
    """Writes a warning message to the console.
    """
    console_output_object.warning(message)

def debug(message):
    """Writes a debugging message to the console.
    """
    console_output_object.debug(message)

def fatal(message):
    """Writes a fatal message to the console.  The default
    implementation raises SystemExit after writing the message.
    """
    console_output_object.fatal(message)
