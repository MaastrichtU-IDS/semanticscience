# Pyro-based trajectory server
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

from TrajectoryInspector import TrajectoryInspector
from Scientific import N as Numeric # to enable pickling of arrays
import Pyro.core, Pyro.naming
import socket, sys

class PyroTrajectoryInspector(Pyro.core.ObjBase, TrajectoryInspector):

    def __init__(self, filename):
        Pyro.core.ObjBase.__init__(self)
        TrajectoryInspector.__init__(self, filename)

    def close(self):
        TrajectoryInspector.close(self)
        PyroDaemon.disconnect(self)


class TrajectoryServer(Pyro.core.ObjBase):

    def __init__(self, hostname, ip_address):
        self.hostname = hostname
        self.ip_address = ip_address
        self.files = {}
        self.exit = 0
        Pyro.core.ObjBase.__init__(self)

    def publishTrajectory(self, filename):
        inspector = PyroTrajectoryInspector(filename)
        self.files[filename] = inspector
        PyroDaemon.connect(inspector,
                           ip_address + ':MMTK:trajectory:' + filename)

    def unpublishTrajectory(self, filename):
        try:
            inspector = self.files[filename]
        except KeyError:
            raise OSError("file not published")
        del self.files[filename]
        inspector.close()

    def stop(self):
        for filename, inspector in self.files.items():
            del self.files[filename]
            inspector.close()
        PyroDaemon.disconnect(self)
        self.exit = 1

Pyro.core.initServer()
PyroDaemon = Pyro.core.Daemon()
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

locator = Pyro.naming.NameServerLocator()
try:
    pyro_ns = locator.getNS()
except (PyroError,socket.error),x:
    pyro_ns = locator.getNS(host=hostname)
PyroDaemon.useNameServer(pyro_ns)

server = TrajectoryServer(hostname, ip_address)
PyroDaemon.connect(server, ip_address + ':MMTK:server')

while 1:
    PyroDaemon.handleRequests(10.)
    if server.exit:
        break
