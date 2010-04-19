import sys
from chimera import runCommand
from SurfaceColor import makeMeshes

proID = sys.argv[1]
jobID = sys.argv[2]
peptideLen = sys.argv[3]
pocketDistance = sys.argv[4]
makeMeshes.makeAllMeshes(proID, jobID, peptideLen, pocketDistance)

runCommand('close session')
runCommand('stop confirmed')
