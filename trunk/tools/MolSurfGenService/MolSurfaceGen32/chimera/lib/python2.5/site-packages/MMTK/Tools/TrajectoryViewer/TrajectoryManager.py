import Pyro.core, Pyro.naming, Pyro.errors
import os, socket, string


server_script = '~/mmtk2/Tools/TrajectoryViewer/TrajectoryServer.py'


class TrajectoryManager:

    def __init__(self):
        Pyro.core.initClient(0)
        locator = Pyro.naming.NameServerLocator()
        self.pyro_ns = locator.getNS()
        self.my_name = socket.gethostname()
        self.my_address = socket.gethostbyname(self.my_name)

    def server(self):
        try:
            uri = self.pyro_ns.resolve(self.my_address+':MMTK:server')
        except Pyro.errors.NamingError:
            return None
        return Pyro.core.getProxyForURI(uri)

    def startServer(self):
        import time
        os.system('python ' + server_script + ' > /dev/null 2>&1 &')
        time.sleep(2)
        
    def stopServer(self):
        server = self.server()
        server.stop()

    def serverList(self):
        servers = []
        for name in self.pyro_ns.status().keys():
            fields = string.split(name, ':')
            if len(fields) == 3 and fields[1] == 'MMTK' \
               and fields[2] == 'server':
                ip_address = fields[0]
                hostname = socket.gethostbyaddr(ip_address)[0]
                servers.append(hostname)
        return servers

    def publish(self, filename):
        filename = os.path.abspath(filename)
        server = self.server()
        if server is None:
            self.startServer()
            server = self.server()
            if server is None:
                raise OSError("couldn't start server")
        server.publishTrajectory(filename)

    def unpublish(self, filename):
        filename = os.path.abspath(filename)
        server = self.server()
        if server is None:
            raise OSError("no server available")
        server.unpublishTrajectory(filename)

    def trajectoryList(self):
        trajectories = []
        for name in self.pyro_ns.status().keys():
            fields = string.split(name, ':')
            if len(fields) == 4 and fields[1] == 'MMTK' \
               and fields[2] == 'trajectory':
                ip_address = fields[0]
                filename = fields[3]
                hostname = socket.gethostbyaddr(ip_address)[0]
                trajectories.append("%s:%s" % (hostname, filename))
        return trajectories

    def trajectoryInspector(self, name):
        colon = string.find(name, ':')
        if colon < 0:
            raise ValueError("not a remote trajectory name")
        ip_address = socket.gethostbyname(name[:colon])
        pyro_name = ip_address+':MMTK:trajectory:'+name[colon+1:]
        uri = self.pyro_ns.resolve(pyro_name)
        return Pyro.core.getProxyForURI(uri)
