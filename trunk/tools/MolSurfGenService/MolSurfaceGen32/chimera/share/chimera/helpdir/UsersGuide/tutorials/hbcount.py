from chimera import runCommand
runCommand("findhbond linewidth 2 color yellow")
from chimera.misc import getPseudoBondGroup
hbonds = len(getPseudoBondGroup("hydrogen bonds").pseudoBonds)
runCommand("2dlabels change mylabel text '%d H-bonds'" % hbonds)
