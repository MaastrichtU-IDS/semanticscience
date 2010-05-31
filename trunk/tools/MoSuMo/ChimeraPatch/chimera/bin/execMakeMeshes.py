import sys
from chimera import runCommand
from SurfaceColor import makeMeshes

proID = sys.argv[5]
jobID = sys.argv[6]
peptideLen = sys.argv[7]
pocketDistance = sys.argv[8]
makeMeshes.makeAllMeshes(proID, jobID, peptideLen, pocketDistance)

runCommand('close session')
runCommand('stop confirmed')
