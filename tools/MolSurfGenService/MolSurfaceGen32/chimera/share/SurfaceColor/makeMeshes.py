import os
import sys
import chimera
from chimera import runCommand, selection, openModels, Molecule
from DockPrep import prep
#from SPARQL import SPARQLWrapper, JSON  #For Query, library not included
from rdflib.Graph import Graph
from rdflib import URIRef, Literal, BNode, Namespace, RDF
curResID = 'none'
curProID = 'none'

meshDir = ''
pocketMap = {}
def makeAllMeshes(proID, jobID, peptideLen=40, pocketDist=5.0):

    global curResID
    global curProID
    global meshDir
    global pocketMap
    global resCount
    global curJobID
    
    #Insure input is a 4 character protein ID
    proID = proID[0:4]

    #Create a new directory for the protein
    meshDir = proID + 'Mesh'
    curProID = proID
    curJobID = jobID
   # os.mkdir(meshDir)
   # os.system("chmod 777 " + meshDir)  
    try:
        #Fetch protein from the PDB
        runCommand('open '+ proID)

        #Initial prep for pocket search
        runCommand('delete solvent')
        runCommand('delete :HOH')

        #Open protein model
        model = openModels.list(modelTypes=[Molecule])[0]
        RES_LIST = model.residues
        resCount = len(RES_LIST)

        #Pocket finding procedure
        chains = []
        counts = []
        index = 0
        print 'Counting Chain Lengths................'
        for res in RES_LIST:
            curChain = str(res.id.chainId)
            if len(chains) == 0:
                chains.append(curChain)
                counts.append(1)
            if curChain != chains[index]:
                index = index + 1
                chains.append(curChain)
                counts.append(1)
            else:
                counts[index] = counts[index] + 1
        
        print 'Finding Peptide Ligand Pockets................'
        for i, chain in enumerate(chains):
            if counts[i] < peptideLen:                           #Less than X amino acids = peptide
                runCommand('~select')
                runCommand('select ligand & :.' + chain)                #Check if actually ligand
                runCommand('select selected zr<' + str(pocketDist))     #Select pocket
                runCommand('~select :/isHet zr<' + str(pocketDist))     #De-select ligand
                runCommand('~select ligand')
                residues = selection.currentResidues()   #Store pocket in memory
                for res in residues:                      
                    if res in pocketMap:
                        pocketMap[res].append('|' + chain) 
                    else:
                        pocketMap[res] = [chain]
        print 'Finding non-Peptide Ligand Pockets................'
        for res in RES_LIST:

            if res.isHet:                                #Check if "heterogenous residue" which includes ligands
                 curResID = str(res.id)
                 runCommand('~select')
                 runCommand('select :' + curResID + ' & ligand')          #Check if actually ligand
                 runCommand('select selected zr<' + str(pocketDist))      #Select pocket
                 runCommand('~select :' + curResID)
                 residues = selection.currentResidues()                   #Store pocket in memory
                 for pocketRes in residues:
                     if pocketRes in pocketMap:
                        pocketMap[pocketRes].append('|' + res.type + '-' + curResID) 
                     else:
                        pocketMap[pocketRes] = [res.type + '-' + curResID] 

        print 'Dock Prep................'
        
        prep(openModels.list(modelTypes=[Molecule]))
        runCommand('delete ligand')
        print '\nRunning Delphi................'
        runCommand('~select')
        runCommand('write format pdb 0 '+ proID + curJobID + '.pdb')  #Write delphi-ready protein with hydrogens
        
        #Create delphi parameter file
        f = open('./param_' + curJobID, 'w')
        f.write('in(pdb,file="'+ proID + curJobID + '.pdb")\n')       #Input/Output files
        f.write('in(siz,file="amber.siz")\n')
        f.write('in(crg,file="amber.crg")\n')
        f.write('out(phi,file="'+ proID + curJobID + '.phi")\n')
        f.write('indi=2\n')                                 #Interior dielectric constant 
        f.write('exdi=80.0\n')                              #Exterior dielectric constant (water)
        f.write('prbrad=1.4\n')
        f.write('salt=0.15\n')                              #Salt concentration and radius
        f.write('ionrad=2.0\n')                             
      #  f.write('nonit=20\n')                               #Non-linear iterations
        f.close()
        os.system("./DELPHI_2004_LINUX_v2/delphi_static param_" + curJobID)      #Run delphi

       # print '\nExporting Mesh................'
        runCommand('select #0')
        runCommand('surface')
        #runCommand('export format X3D ./' + proID + '.x3d') # Prints raw X3D file. 
        
        print '\nOpening Delphi Data................'
        runCommand('open '+ proID + curJobID + '.phi')
        runCommand('scolor #0 volume #1 cmap -1,red:0,white:1,blue;')
        
        print '\nRemoving Temp Files................'
        os.remove("./" + proID + curJobID + '.pdb')
        os.remove("./" + proID + curJobID + '.phi')
        os.remove('./param_' + curJobID)
        print '\nDONE: ' + proID
    except:
        f = open("./" + 'ErrorLog' + curJobID + '.txt', 'w')
        f.write(proID + ' error: ' + str(sys.exc_info()[0]) + str(sys.exc_info()[1]) + '\n')
        f.close()
        raise

    return

#Procedure called from surface coloring method
def printVertices(colorMap):
    global curProID
    global curJobID
    global meshDir
    global pocketMap
    global resCount

    print '\nCreating Vertex Annotation................'
    
    # Collect surface vertex chain id, residue id, and vertex x,y,z coordinates.
    slist = chimera.openModels.list(modelTypes=[chimera.MSMSModel])
    data = []
    faceData = []
    faces = []
    for s in slist:
        va, faces = s.surface_piece.geometry           # vertex and triangle arrays
        na = s.surface_piece.normals
        values, outside = colorMap.volume_values(s.surface_piece) #Get electrostatic charge values

        for i,v in enumerate(va):
            x,y,z = v
            atom = s.atomMap[i]
            elecPot = values[i]
            r = atom.residue
            pockets = ''
            if r in pocketMap:
                for pocket in pocketMap[r]:
                    pockets = pockets + pocket
            data.append((r.id.chainId, r.id.position, r.type, x, y, z, na[i][0], na[i][1], na[i][2], elecPot, pockets))

	for i,faceVerts in enumerate(faces):
            faceData.append((faceVerts[0],faceVerts[1],faceVerts[2]))
                

#    data.sort()
        
    # Create text with one line per vertex.
    lines = ['%3s\t%3d\t%3s\t%10.6f\t%10.6f\t%10.6f\t%6.6f\t%6.6f\t%6.6f\t%10.8f\t%10s' % vinfo for vinfo in data]
    faceLines = ['%5d\t%5d\t%5d' % vinfo for vinfo in faceData]
    text = '\n'.join(lines)
    text = text + '\n' + '\n'.join(faceLines)
    
    #Write out to file
    f = open('./Output-' + curJobID + '.txt', 'w')
    f.write(text)
    f.close()
    
    return
