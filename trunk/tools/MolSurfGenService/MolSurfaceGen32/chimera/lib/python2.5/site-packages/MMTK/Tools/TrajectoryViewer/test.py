import Pyro.core, Pyro.naming
import socket, string
Pyro.core.initClient(0)
locator = Pyro.naming.NameServerLocator()
pyro_ns = locator.getNS()

def inspector(trajectory):
    colon = string.find(trajectory, ':')
    ip_address = socket.gethostbyname(trajectory[:colon])
    name = ip_address+':MMTK:trajectory:'+trajectory[colon+1:]
    uri = pyro_ns.resolve(name)
    return Pyro.core.getProxyForURI(uri)

i = inspector('p-101.para:/scratch/hinsen/lysozyme_equilibration_100bar_300K.nc')

step = i.readScalarVariable('step')
