import chimera
from chimera import replyobj
from chimera.molEdit import addBond
from chimera.molEdit import addDihedralAtom
from chimera.molEdit import addAtom
from chimera.bondGeom import bondPositions

DIST_N_C = 1.335
DIST_CA_N = 1.449
DIST_C_CA = 1.522
DIST_C_O = 1.229

class AddAAError(Exception):
	"""Error while adding amino acid"""
	pass

def isLastRes(res):
    c_at = res.atomsMap['C']
    c_at = c_at[0]
    
    res_id = res.id.position
    
    for at in c_at.neighbors:
        if not at.residue.id.position == res_id:
            return False
    return True
 

def cleanUp(mol, new_res, atoms):
    for a in atoms:
        mol.deleteAtom(a)

    mol.deleteResidue(new_res)


def getBFactor(mol):
    bfactor = None

    for a in mol.atoms:
        try:
            if bfactor is None or a.bfactor > bfactor:
                bfactor = a.bfactor
        except AttributeError:
            pass

    return bfactor
    
    
def getBboneAtom(res, atom_name):
    """find atom of type 'atom' in residue 'res' with
    the highest occupancy value"""

    if not res.atomsMap.has_key(atom_name):
        return None
    
    match_ats  = res.atomsMap[atom_name]
    match_ats.sort(lambda x,y: cmp(x.occupancy,y.occupancy))
    return match_ats[0]


def getLastResidue(after_res):
    ## get a reference to the residue specified by the
    ## after_res argument, and make sure it is the last
    ## one in the chain
    from chimera import selection
    sel_obj = selection.OSLSelection(after_res)

    sel_res      =  sel_obj.residues()
    num_res_spec =  len(sel_res)

    if num_res_spec == 0:
        raise AddAAError, "Couldn't find valid residue based on atom spec \"%s\"" % after_res
    if num_res_spec > 1:
        raise AddAAError, "Too many residues specified: " \
              "%s specifies %d residues" \
              % (after_res, num_res_spec)
                       
    ## last_res represents the last residue of the chain
    ## (i.e. the one we're adding on to!)
    last_res = sel_res[0]
    if not isLastRes(last_res):
        raise AddAAError, "Can only add to last residue!"

    return last_res


def pruneLastResidue(last_res):

    last_C = last_res.atomsMap['C'][0]

    to_prune   = [a for a in last_C.neighbors \
                  if not (a.name=='CA' or a.name=='O')]
    if not to_prune:
        ## nothing there to take off
        return
    elif len(to_prune) > 1:
        ## don't recognize configuration of 'C's bond partners
        raise AddAAError, "No suitable position to add new amino acid"
    else:
        to_prune = to_prune[0]

    if not ( to_prune.neighbors == [last_C] ):
        raise AddAAError, "No suitable position to add new amino acid"

    last_res.molecule.deleteAtom(to_prune)
    

def reposLastO(last_res, last_bbone_ats, atom_drawMode, bond_drawMode):
    ## reposition the last residue's 'O' atom
    last_O = getBboneAtom(last_res, 'O')
    last_res.molecule.deleteAtom(last_O)

    last_C  = last_bbone_ats['C']
    last_CA = last_bbone_ats['CA']
    
    old_O_bond_pos = bondPositions(bondee   = last_C.coord(),
                                   geom     = chimera.Atom.Planar,
                                   bondLen  = 1.229,
                                   bonded   = [a.coord() for a in last_C.neighbors]
                                   )

    ## should only be one spot left
    old_O_bond_pos = old_O_bond_pos[0]
    new_O = addAtom('O', chimera.Element(8), last_res, old_O_bond_pos)
    new_O.drawMode = atom_drawMode
    addBond(new_O, last_C, drawMode=bond_drawMode)

    return new_O


def addNewN(last_bbone_ats, new_res, **kw):

    ## add the N atom of new residue's backbone to the last residue
    last_C = last_bbone_ats['C']

    new_N_bond_pos = bondPositions(bondee  =  last_C.coord(),
                                   geom    =  chimera.Atom.Planar,
                                   bondLen =  DIST_N_C,
                                   bonded  =  [a.coord() for a in last_C.neighbors]
                                   )
    
    use_point = new_N_bond_pos[0]
    new_N = addAtom('N', chimera.Element(7), new_res, use_point)
    new_N.drawMode = kw['atomDrawMode']
    new_N.bfactor  = kw['bFactor']

    addBond(last_C, new_N, drawMode=kw['bondDrawMode'])

    return new_N

    
def addNewCA(last_bbone_ats, new_res, **kw):
    last_CA = last_bbone_ats['CA']
    last_C  = last_bbone_ats['C']
    last_O  = last_bbone_ats['O']

    new_N = new_res.atomsMap['N'][0]
    
    ## add the CA atom (not dihedral!)
    ## first, find the location for the new CA atom
    new_CA_bond_pos = bondPositions(bondee  =  new_N.coord(),
                                    geom    =  chimera.Atom.Planar,
                                    bondLen =  DIST_CA_N,
                                    bonded  =  [a.coord() for a in new_N.neighbors],
                                    coPlanar=  [last_CA.coord(), last_O.coord()]
                                    )
    
    
    shortest_point = getShortestPoint(last_O.coord(), new_CA_bond_pos)
                      
    new_CA = addAtom('CA', chimera.Element(6), new_res, shortest_point)
    new_CA.drawMode = kw['atomDrawMode']
    new_CA.bfactor  = kw['bFactor']

    addBond(new_N, new_CA, drawMode=kw['bondDrawMode'])

    return new_CA


def addNewC(last_bbone_ats, new_res, phi, **kw):

    last_C = last_bbone_ats['C']

    new_CA = new_res.atomsMap['CA'][0]
    new_N  = new_res.atomsMap['N'][0]

    new_C = addDihedralAtom('C', chimera.Element(6), new_CA, new_N,
                            last_C, DIST_C_CA, 109.5, phi, residue=new_res)
    new_C.drawMode = kw['atomDrawMode']
    new_C.bfactor  = kw['bFactor']

    addBond(new_CA, new_C, drawMode=kw['bondDrawMode'])

    return new_C



def addNewOs(new_res, psi, **kw):

    new_N  = new_res.atomsMap['N'][0]
    new_CA = new_res.atomsMap['CA'][0]
    new_C  = new_res.atomsMap['C'][0]

    new_OXT = addDihedralAtom('OXT', chimera.Element(8), new_C, new_CA, new_N,
                              DIST_C_O, 114, psi, residue=new_res)
    new_OXT.drawMode   = kw['atomDrawMode']
    new_OXT.bfactor    = kw['bFactor']

    addBond(new_OXT, new_C, drawMode=kw['bondDrawMode'])
    
    avail_bond_pos = bondPositions(bondee  =  new_C.coord(),
                                   geom    =  chimera.Atom.Planar,
                                   bondLen =  DIST_C_O,
                                   bonded  =  [a.coord() for a in new_C.neighbors]
                                   )

    use_point = avail_bond_pos[0]

    new_O = addAtom('O', chimera.Element(8), new_res, use_point)
    new_O.drawMode   = kw['atomDrawMode']
    new_O.bfactor    = kw['bFactor']

    addBond(new_O, new_C, drawMode=kw['bondDrawMode'])
                                
    return new_O, new_OXT



def getPhiPsiVals(conformation):

    phi = None
    psi = None

    ## get correct phi and psi values based on conformation    
    if not conformation:
        phi = 180
        psi = 180

    else:
        ## can conformation include phi and psi values ?
        if isinstance(conformation, tuple):
            if len(conformation) == 2:
                phi, psi = [float(p) for p in conformation]
            else:
                raise AddAAError, "Must specify both phi and psi values or neither"
            
                
        elif conformation.lower() == 'ext':
            phi = 180
            psi = 180

        elif conformation.lower() == 'alpha':
            phi = -57
            psi = -47

        elif conformation.lower() == 'abeta':
            phi = -139
            psi =  135
        
        elif conformation.lower() == 'pbeta':
            phi = -119
            psi =  113

        else:
            raise AddAAError, "Conformation must be one of " \
                  "\"alpha\", \"abeta\", \"pbeta\", "        \
                  " \"ext\" or \"phi,psi\""   
        
    return phi,psi
    

def addAA(residue_type, residue_seq, last_res, conformation=None):
    """add an amino acid to a model.
    """
    
    phi,psi = getPhiPsiVals(conformation)

    if not isLastRes(last_res):
        raise AddAAError, "Can only add to last residue."
  
    last_bbone_ats = {}
    
    ## find 'C' atom of last residue
    last_C = getBboneAtom(last_res, 'C')
    if not last_C:
        raise AddAAError, "Couldn't find 'C' backbone atom of last residue"
    else:
        last_bbone_ats['C'] = last_C

    ## find 'CA' atom of last residue
    last_CA = getBboneAtom(last_res, 'CA')
    if not last_CA:
        raise AddAAError, "Couldn't find 'CA' backbone atom of last residue"
    else:
        last_atom_drawMode = last_CA.drawMode
        last_bond_drawMode = last_CA.bondsMap[last_C].drawMode

        last_bbone_ats['CA'] = last_CA

    ## find 'N' atom of last residue
    last_N = getBboneAtom(last_res, 'N')
    if not last_N:
        raise AddAAError, "Couldn't find 'N' backbone atom of last residue"
    else:
        last_bbone_ats['N'] = last_N

    ## find 'O' atom of last residue
    last_O = getBboneAtom(last_res, 'O')
    if not last_O:
        raise AddAAError, "Couldn't find 'O' backbone atom of last residue"
    else:
        last_bbone_ats['O'] = last_O
    
    ## make a new residue
    insert_char = residue_seq[-1]
    if insert_char.isalpha():
        ## insertion specified
        residue_seq = residue_seq[:-1]
    else:
        insert_char = ' '
    if residue_seq.isdigit():
        residue_seq = int(residue_seq)
    else:
        raise AddAAError, "Residue sequence argument can contain at most one insertion character"

    mol = last_res.molecule
    mrid = chimera.MolResId(last_res.id.chainId,
                            residue_seq,
                            insert = insert_char)
    if mol.findResidue(mrid):
        raise AddAAError, "Can't add amino acid, model already contains residue with sequence '%s'." % \
              residue_seq
    
    new_res = mol.newResidue(residue_type, mrid, neighbor=last_res, after=True)
                            
    if conformation == 'alpha':
        new_res.isHelix = True
    elif conformation in ('abeta', 'pbeta'):
        new_res.isSheet = True

    bFac = getBFactor(mol)

    ## now delete any terminal atoms from the last residue, if there is one
    ## there.
    try:
        pruneLastResidue(last_res)
    except AddAAError, what:
        cleanUp(mol, new_res, [])
        raise AddAAError, what

    
    ## add the N atom for the new residue's backbone
    new_N = addNewN(last_bbone_ats, new_res,
                    atomDrawMode = last_atom_drawMode,
                    bondDrawMode = last_bond_drawMode,
                    bFactor      = bFac)
                    
    ## add the carbon alpha atom for the new residue's backbone
    new_CA = addNewCA(last_bbone_ats, new_res,
                      atomDrawMode = last_atom_drawMode,
                      bondDrawMode = last_bond_drawMode,
                      bFactor      = bFac)
                      
    ## add the carbon aton for the new residue's backbone
    new_C = addNewC(last_bbone_ats, new_res, phi,
                    atomDrawMode = last_atom_drawMode,
                    bondDrawMode = last_bond_drawMode,
                    bFactor      = bFac)
                    
    ## add the oxygen for the new residue's backbone
    new_O, new_OXT = addNewOs(new_res, psi,
                              atomDrawMode = last_atom_drawMode,
                              bondDrawMode = last_bond_drawMode,
                              bFactor      = bFac)
                              
        
    ## swap residues type
    import Midas
    try:
        Midas.swapres(residue_type, sel=new_res.oslIdent(), bfactor=bFac)
    except:
        cleanUp(mol, new_res, [new_N, new_CA, new_C, new_O, new_OXT])
        
        import sys
        error, val = sys.exc_info()[:2]
        raise AddAAError, val
        

def getShortestPoint(ref_point, point_list):

    shortest_point = None
    shortest_dist  = None
    
    for p in point_list:
        dist = chimera.distance(p, ref_point)
        if (not shortest_dist) or dist < shortest_dist:
            shortest_point = p
            shortest_dist  = dist

    return shortest_point
