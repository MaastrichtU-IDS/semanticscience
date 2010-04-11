# Contributed by Thomas Margraf, August 13, 2009.
from ctypes import Structure, Union, c_int, c_uint, c_void_p, cdll, byref
class MotionEvent(Structure):
    _fields_ = [("type" , c_int),
    ("x" , c_int),
    ("y" , c_int),
    ("z" , c_int),
    ("rx" , c_int),
    ("ry" , c_int),
    ("rz" , c_int),
    ("period" , c_uint),
    ("data" , c_void_p)]

class ButtonEvent(Structure):
    _fields_ = [("type" , c_int),
    ("press" , c_int),
    ("bnum" , c_int)]

class Event(Union):
    _fields_ = [("type", c_int),
    ("spnav_event_motion", MotionEvent),
    ("spnav_event_button", ButtonEvent)]

class Space_Device_Linux:
    def __init__(self):
        self.max_delay = 0.2
        self.min_lag = 1e20
        from os import path, environ
        lib = path.join(environ['CHIMERA'], 'lib', 'libspnav.so.0.1')
        self.snav = cdll.LoadLibrary(lib)
        ret = self.snav.spnav_open()
	if ret is -1:
            raise EnvironmentError, "Can't access space navigator, display inaccessible"
            return None
        else: 
            self.s = Event(1, MotionEvent())

    def last_event(self):
        self.s = s = Event(1, MotionEvent())
        ret = self.snav.spnav_poll_event(byref(s))
        if ret is None:
            return None
        buttons = []
        trans = [0,0,0]
        rot = [0,0,0]
        if s.type is 2:
            b = s.spnav_event_button
            if b.bnum is 0 and b.press is 1:
                buttons.append('N1')
            if b.bnum is 1 and b.press is 1:
                buttons.append('N2')
        elif s.type is 1:
            m = s.spnav_event_motion
            trans = (m.x, m.y, -m.z)
            rot = (m.rx, m.ry, -m.rz)
        self.snav.spnav_remove_events(1)
        return (rot, trans, buttons)
