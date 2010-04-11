# -----------------------------------------------------------------------------
# Dialog for making copies of PDB molecule to fill out crystal unit cell.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Unit_Cell_Dialog(ModelessDialog):

  title = 'Unit Cell'
  name = 'unit cell'
  buttons = ('Options', 'Close',)
  help = 'ContributedSoftware/unitcell/unitcell.html'
  
  def fillInUI(self, parent):

    self.molecules = []
    self.add_model_handler = None
    self.remove_model_handler = None
    
    import Tkinter
    from CGLtk import Hybrid
    
    row = 0

    mm = Hybrid.Option_Menu(parent, 'Molecule: ')
    mm.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    mm.add_callback(self.molecule_menu_cb)
    self.molecule_menu = mm

    labels = []
    for text in ('Space group: ',
                 'Cell size: ',
                 'Cell angles: ',
                 'Number of SMTRY matrices: ',
                 'Number of space group symmetries: ',
                 'Number of MTRIX matrices: ',
                 ):
      lbl = Tkinter.Label(parent, text = text)
      lbl.grid(row = row, column = 0, sticky = 'w')
      row = row + 1
      labels.append(lbl)
    (self.space_group,
     self.cell_size,
     self.cell_angles,
     self.smtry_count,
     self.sg_smtry_count,
     self.mtrix_count,
     ) = labels

    op = Hybrid.Popup_Panel(parent)
    opf = op.frame
    opf.grid(row = row, column = 0, sticky = 'news')
    opf.grid_remove()
    opf.columnconfigure(0, weight=1)
    self.options_panel = op.panel_shown_variable
    row += 1
    orow = 0

    cb = op.make_close_button(opf)
    cb.grid(row = orow, column = 1, sticky = 'e')
    
    usr = Hybrid.Checkbutton(opf, 'Use SMTRY records in PDB header', True)
    usr.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.use_smtry_records = usr.variable
    
    ucr = Hybrid.Checkbutton(opf, 'Use CRYST1 record if SMTRY records are missing', True)
    ucr.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.use_cryst1_smtry = ucr.variable
    
    umr = Hybrid.Checkbutton(opf, 'Use MTRIX records for non-crystallographic symmetry', True)
    umr.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.use_mtrix_records = umr.variable

    co = Hybrid.Entry(opf, 'Cell origin ', 12, '0 0 0')
    co.frame.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.grid_orig = co.variable
    co.entry.bind('<KeyPress-Return>', self.origin_change_cb)

    nc = Hybrid.Entry(opf, 'Number of cells ', 12, '1 1 1')
    nc.frame.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.ncells = nc.variable
    nc.entry.bind('<KeyPress-Return>', self.make_unit_cell_cb)

    br = Hybrid.Button_Row(parent, '',
                           (('Make copies', self.make_unit_cell_cb),
                            ('Outline', self.show_outline_cb),
                            ('Delete copies', self.close_unit_cell_cb),
                            ))
    br.frame.grid(row = row, column = 0, sticky = 'e')
    row = row + 1
    
  # ---------------------------------------------------------------------------
  #
  def map(self, event):

    self.update_molecule_menu()

    if self.add_model_handler == None:
      om = chimera.openModels
      ah = om.addAddHandler(self.model_list_changed_cb, None)
      self.add_model_handler = ah
      rh = om.addRemoveHandler(self.model_list_changed_cb, None)
      self.remove_model_handler = rh
    
  # ---------------------------------------------------------------------------
  #
  def unmap(self, event):

    if self.add_model_handler:
      om = chimera.openModels
      om.deleteAddHandler(self.add_model_handler)
      self.add_model_handler = None
      om.deleteRemoveHandler(self.remove_model_handler)
      self.remove_model_handler = None
    
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())
    
  # ---------------------------------------------------------------------------
  #
  def molecule_menu_cb(self):

    m = self.menu_molecule()

    from PDBmatrices import crystal_parameters
    cp = crystal_parameters(pdb_headers(m))
    if cp:
      a, b, c, alpha_rad, beta_rad, gamma_rad, space_group, zvalue = cp
      import math
      radians_to_degrees = 180 / math.pi
      alpha = radians_to_degrees * alpha_rad
      beta = radians_to_degrees * beta_rad
      gamma = radians_to_degrees * gamma_rad
      sg = space_group
      cs = '%7.3f %7.3f %7.3f' % (a,b,c)
      ca = '%6.2f %6.2f %6.2f' % (alpha,beta,gamma)
    else:
      sg = cs = ca = ''

    from PDBmatrices import pdb_space_group_matrices
    sg_sym = pdb_space_group_matrices(pdb_headers(m))
    if sg_sym:
      sgsc = '%d' % len(sg_sym)
    else:
      sgsc = ''

    self.space_group['text'] = 'Space group: ' + sg
    self.cell_size['text'] = 'Cell size: ' + cs
    self.cell_angles['text'] = 'Cell angles: ' + ca
    self.sg_smtry_count['text'] = 'Number of space group symmetries: ' + sgsc

    from PDBmatrices import pdb_smtry_matrices
    sm = pdb_smtry_matrices(pdb_headers(m))
    self.smtry_count['text'] = 'Number of SMTRY matrices: %d' % len(sm)

    from PDBmatrices import pdb_mtrix_matrices
    mm = pdb_mtrix_matrices(pdb_headers(m), add_identity = False)
    self.mtrix_count['text'] = 'Number of MTRIX matrices: %d' % len(mm)

  # ---------------------------------------------------------------------------
  #
  def menu_molecule(self):

    mname = self.molecule_menu.variable.get()
    for m in self.molecules:
      if m.name == mname:
        return m
    return None
    
  # ---------------------------------------------------------------------------
  #
  def make_unit_cell_cb(self, event = None):

    m = self.menu_molecule()
    if m == None:
      return
    
    tflist = self.transforms(m)
    place_molecule_copies(m, tflist)
    remove_extra_copies(m, len(tflist))
    
  # ---------------------------------------------------------------------------
  #
  def show_outline_cb(self):

    m = self.menu_molecule()
    if m == None:
      return

    name = self.outline_model_name(m)
    om = find_model_by_name(name)       # Close outline if shown
    if om:
      from chimera import openModels
      openModels.close([om])
    else:
      self.show_outline_model(m)

  # ---------------------------------------------------------------------------
  #
  def show_outline_model(self, m, om = None):

    from PDBmatrices import crystal_parameters, cell_origin
    cp = crystal_parameters(pdb_headers(m))
    if cp == None:
      return
    a, b, c, alpha, beta, gamma, space_group, zvalue = cp

    from PDBmatrices.crystal import unit_cell_axes
    axes = unit_cell_axes(a, b, c, alpha, beta, gamma)
    from Molecule import molecule_center
    mc = molecule_center(m)
    origin = cell_origin(self.grid_origin(), axes, mc)
    color = (1,1,1)                     # white

    b = outline_box(origin, axes, color, om)
    b.name = self.outline_model_name(m)
    if om is None:
      from chimera import openModels
      openModels.add([b], sameAs = m)

  # ---------------------------------------------------------------------------
  #
  def outline_model_name(self, molecule):

    return molecule.name + ' unit cell outline'
    
  # ---------------------------------------------------------------------------
  #
  def origin_change_cb(self, event):

    m = self.menu_molecule()
    if m == None:
      return

    om = find_model_by_name(self.outline_model_name(m))
    if om:
      self.show_outline_model(m, om)

    if find_model_by_name(m.name + ' #2'):
      self.make_unit_cell_cb()
    
  # ---------------------------------------------------------------------------
  # Find origin of cell in unit cell grid containing specified point.
  #
  def grid_origin(self):

    try:
      gorigin = [float(s) for s in self.grid_orig.get().split()]
    except ValueError:
      # TODO: should warn about unparsable origin values
      gorigin = (0,0,0)

    if len(gorigin) != 3:
      gorigin = (0,0,0)

    return gorigin
  
  # ---------------------------------------------------------------------------
  #
  def number_of_cells(self):

    try:
      nc = [int(s) for s in self.ncells.get().split()]
    except ValueError:
      # TODO: should warn about unparsable origin values
      nc = (1,1,1)

    if len(nc) != 3:
      nc = (1,1,1)

    return nc

  # ---------------------------------------------------------------------------
  #
  def transforms(self, molecule):

    import PDBmatrices
    
    sm = []
    h = pdb_headers(molecule)
    if self.use_smtry_records.get():
      sm = PDBmatrices.pdb_smtry_matrices(h)
    if len(sm) == 0 and self.use_cryst1_smtry.get():
      sm = PDBmatrices.pdb_space_group_matrices(h)

    from Matrix import identity_matrix, matrix_products
    mm = [identity_matrix()]
    if self.use_mtrix_records.get():
      mm = PDBmatrices.pdb_mtrix_matrices(h)
      
    if sm:
      tflist = matrix_products(sm, mm)
    else:
      tflist = mm

    # Adjust transforms so centers of models are in unit cell box
    from Molecule import unit_cell_parameters, molecule_center
    uc = unit_cell_parameters(molecule)
    if uc:
      mc = molecule_center(molecule)
      tflist = PDBmatrices.pack_unit_cell(uc, self.grid_origin(), mc, tflist)

    # Make multiple unit cells
    nc = self.number_of_cells()
    if nc != (1,1,1):
      tflist = PDBmatrices.unit_cell_translations(uc, nc, tflist)

    return tflist
  
  # ---------------------------------------------------------------------------
  #
  def close_unit_cell_cb(self):

    m = self.menu_molecule()
    if m == None:
      return

    mlist = chimera.openModels.list(modelTypes = [chimera.Molecule])
    copies = [mc for mc in mlist if (hasattr(mc, 'openedAs') and
                                     mc.openedAs == m.openedAs and
                                     mc != m)]
    chimera.openModels.close(copies)
    
  # ---------------------------------------------------------------------------
  #
  def model_list_changed_cb(self, *args):

    self.update_molecule_menu()
    
  # ---------------------------------------------------------------------------
  #
  def update_molecule_menu(self):

    molecules = chimera.openModels.list(modelTypes = [chimera.Molecule])

    # Keep only one copy of molecules that have multiple opened copies.
    # Keep the copy with the shortest name.
    oatable = {}
    for m in molecules:
      if hasattr(m, 'openedAs'):
        if ((not m.openedAs in oatable) or
            len(m.name) < len(oatable[m.openedAs].name)):
          oatable[m.openedAs] = m
    mlist = oatable.values()
    mlist.sort(lambda m1, m2: cmp(m1.name, m2.name))

    if mlist != self.molecules:
      mm = self.molecule_menu
      choice = mm.variable.get()
      mm.remove_all_entries()
      for m in mlist:
        mm.add_entry(m.name)
      self.molecules = mlist
      if not choice in map(lambda m: m.name, mlist):
        if mlist:
          choice = mlist[0]
        else:
          choice = ''
        mm.variable.set(choice)

    if mlist and self.menu_molecule() == None:
      self.molecule_menu.variable.set(mlist[0].name)

# -----------------------------------------------------------------------------
#
def pdb_headers(molecule):

  if hasattr(molecule, 'pdbHeaders'):
    return molecule.pdbHeaders
  return {}

# -----------------------------------------------------------------------------
#
def place_molecule_copies(m, tflist):
  
  path, file_type, default_file_type, prefixable_type = m.openedAs
    
  from Molecule import copy_molecule, transform_atom_positions
  from Matrix import is_identity_matrix
  for i,tf in enumerate(tflist):
    if is_identity_matrix(tf):
      continue
    name = m.name + (' #%d' % (i+1))
    c = find_model_by_name(name)
    if c is None:
      c = copy_molecule(m)
      c.name = name
      transform_atom_positions(c.atoms, tf)
      chimera.openModels.add([c])
    else:
      transform_atom_positions(c.atoms, tf, m.atoms)

# -----------------------------------------------------------------------------
#
def remove_extra_copies(m, nkeep):

  clist = []
  while True:
    name = m.name + (' #%d' % (len(clist)+nkeep+1))
    c = find_model_by_name(name)
    if c is None:
      break
    clist.append(c)
  from chimera import openModels
  openModels.close(clist)

# -----------------------------------------------------------------------------
#
def find_model_by_name(name):

  import chimera
  mlist = chimera.openModels.list()
  for m in mlist:
    if m.name == name:
      return m
  return None

# -----------------------------------------------------------------------------
# Centered at origin.
#
def outline_box(origin, axes, rgb, surface_model):

  a0, a1, a2 = axes
  from numpy import array, add
  c000 = array(origin)
  c100 = add(c000, a0)
  c010 = add(c000, a1)
  c001 = add(c000, a2)
  c110 = add(c100, a1)
  c101 = add(c100, a2)
  c011 = add(c010, a2)
  c111 = add(a0, c011)
  vlist = (c000, c001, c010, c011, c100, c101, c110, c111)
  qlist = ((0,4,5), (5,1,0), (0,2,6), (6,4,0),
           (0,1,3), (3,2,0), (7,3,1), (1,5,7),
           (7,6,2), (2,3,7), (7,5,4), (4,6,7))

  b = 8 + 2 + 1    # Bit mask, 8 = show triangle, edges are bits 4,2,1
  hide_diagonals = (b,b,b,b,b,b,b,b,b,b,b,b)

  if surface_model:
    # Replace the geometry of the first piece.
    p = surface_model.surfacePieces[0]
    p.geometry = vlist, qlist
    p.triangleAndEdgeMask = hide_diagonals
  else:
    import _surface
    surface_model = _surface.SurfaceModel()
    rgba = tuple(rgb) + (1,)
    piece = surface_model.addPiece(vlist, qlist, rgba)
    piece.displayStyle = piece.Mesh
    piece.useLighting = False
    piece.triangleAndEdgeMask = hide_diagonals
    piece.outline_box = True

  return surface_model

# -----------------------------------------------------------------------------
#
def show_unit_cell_dialog():

  from chimera import dialogs
  return dialogs.display(Unit_Cell_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Unit_Cell_Dialog.name, Unit_Cell_Dialog, replace = 1)
