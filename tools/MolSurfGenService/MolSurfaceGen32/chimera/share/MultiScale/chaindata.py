# -----------------------------------------------------------------------------
# Cached chain data.
#
class Multiscale_Chain_Data:

  def __init__(self, molecule):

    self.molecule = molecule

    self.chain_id_list = None
    self.chain_table = None

  # ---------------------------------------------------------------------------
  #
  def chain(self, chain_id, create = True):

    if self.chain_table is None:
      if create:
        ct = {}
        for cid in self.chain_ids():
          ct[cid] = Chain_Data(cid)
        self.chain_table = ct
      else:
        return None
    return self.chain_table.get(chain_id, None)

  # ---------------------------------------------------------------------------
  #
  def chain_ids(self):

    if self.chain_id_list is None:
      self.chain_id_list = self.compute_chain_ids()
    return self.chain_id_list

  # ---------------------------------------------------------------------------
  #
  def compute_chain_ids(self):

    ct = {}
    m = self.molecule
    for r in m.residues:
      ct[r.id.chainId] = 1
    clist = ct.keys()
    clist.sort()
    return clist
    
  # ---------------------------------------------------------------------------
  #
  def chain_atoms(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      return []
    if c.atoms is None:
      self.compute_chain_atoms()
    return c.atoms
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_atoms(self):

    cat = {}
    for a in self.molecule.atoms:
        cid = a.residue.id.chainId
        if cid in cat:
            cat[cid].append(a)
        else:
            cat[cid] = [a]
    for cid in self.chain_ids():
      self.chain(cid).atoms = cat.get(cid,[])
    
  # ---------------------------------------------------------------------------
  #
  def chain_bonds(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      return []
    if c.bonds is None:
      self.compute_chain_bonds()
    return c.bonds
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_bonds(self):

    cbt = {}
    for cid in self.chain_ids():
      cbt[cid] = []
      
    for b in self.molecule.bonds:
      a1, a2 = b.atoms
      cid1 = a1.residue.id.chainId
      cid2 = a1.residue.id.chainId
      if cid1 == cid2:
        cbt[cid1].append(b)

    for cid in self.chain_ids():
      self.chain(cid).bonds = cbt.get(cid, [])
    
  # ---------------------------------------------------------------------------
  #
  def chain_residues(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      return []
    if c.residues is None:
      self.compute_chain_residues()
    return c.residues
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_residues(self):

    crt = {}
    for r in self.molecule.residues:
      cid = r.id.chainId
      if cid in crt:
        crt[cid].append(r)
      else:
        crt[cid] = [r]
    for cid in self.chain_ids():
      self.chain(cid).residues = crt.get(cid, [])
    
  # ---------------------------------------------------------------------------
  #
  def chain_sequence(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      return ()
    if c.sequence is None:
      c.sequence = self.compute_chain_sequence(chain_id)
    return c.sequence
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_sequence(self, chain_id):

    rlist = list(self.chain_residues(chain_id))
    rlist.sort()
    rtypes = tuple(map(lambda r: r.type, rlist))
    return rtypes
    
  # ---------------------------------------------------------------------------
  #
  def chain_atom_xyz(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      from numpy import zeros, single as floatc
      return zeros((0,3),floatc)
    if c.atom_xyz is None:
      c.atom_xyz = self.compute_chain_atom_xyz(chain_id)
    return c.atom_xyz
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_atom_xyz(self, chain_id):
      
    alist = self.chain_atoms(chain_id)
    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(alist)
    return xyz
    
  # ---------------------------------------------------------------------------
  #
  def chain_atom_radii(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      from numpy import zeros, single as floatc
      return zeros((0,),floatc)
    if c.atom_radii is None:
      c.atom_radii = self.compute_chain_atom_radii(chain_id)
    return c.atom_radii
    
  # ---------------------------------------------------------------------------
  #
  def compute_chain_atom_radii(self, chain_id):
      
    alist = self.chain_atoms(chain_id)
    n = len(alist)
    from numpy import zeros, single as floatc
    r = zeros((n,), floatc)
    for a in range(n):
        r[a] = alist[a].radius
    return r

  # ---------------------------------------------------------------------------
  #
  def chain_has_only_ca_atoms(self, chain_id):

    c = self.chain(chain_id)
    if c is None:
      return True
    if c.has_only_ca_atoms is None:
      c.has_only_ca_atoms = self.compute_chain_has_only_ca_atoms(chain_id)
    return c.has_only_ca_atoms

  # ---------------------------------------------------------------------------
  #
  def compute_chain_has_only_ca_atoms(self, chain_id):
      
    alist = self.chain_atoms(chain_id)
    for a in alist:
        if a.name != 'CA':
            return False
    return True

  # ---------------------------------------------------------------------------
  # Handles deleted atoms.  Return true if change detected.
  #
  def update_cached_chain_data(self, chain_id):

    c = self.chain(chain_id, create = False)
    if c is None:
      return False
    if c.atoms is None or len([a for a in c.atoms if a.__destroyed__]) == 0:
      return False
    c.clear()
    return True

# -----------------------------------------------------------------------------
#
class Chain_Data:

  def __init__(self, chain_id):

    self.chain_id = chain_id
    self.clear()

  def clear(self):

    self.atoms = None
    self.bonds = None
    self.residues = None
    self.sequence = None
    self.atom_xyz = None
    self.atom_radii = None
    self.has_only_ca_atoms = None
