import sys
from chimera import runCommand
from SurfaceColor import makeMeshes

proID = sys.argv[1]
peptideLen = sys.argv[2]
pocketDistance = sys.argv[3]
makeMeshes.makeAllMeshes(proID, peptideLen, pocketDistance)

runCommand('close session')
runCommand('stop confirmed')
