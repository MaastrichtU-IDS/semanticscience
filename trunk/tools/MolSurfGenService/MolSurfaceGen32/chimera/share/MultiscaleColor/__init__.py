# ----------------------------------------------------------------------------
# Command to color multiscale surfaces to match atom colors including coloring
# components that do not have loaded atoms.  This was for Padmaja Natarajan
# to color virus capsids according to PDB file b-factor values which could
# reperesent non-b-factor attributes.
#
    
# -----------------------------------------------------------------------------
# Command syntax: msc <multiscale-surface-id> <atom-spec> <distance>
#
def multiscale_color(cmdname, args):
    
  fields = args.split()

  if len(fields) != 3:
    from Midas.midas_text import error
    error('%s requires 3 arguments, got %d: %s <multiscale-surface-id> <atom-spec> <coloring-distance>' % (cmdname, len(fields), cmdname))
    return

  surf_spec, atom_spec, dist = fields

  ms_models = parse_multiscale_models(surf_spec, cmdname)
  if len(ms_models) == 0:
    return

  atoms = parse_atom_specifier(atom_spec, cmdname)
  if len(atoms) == 0:
    return

  # Parse coloring distance
  try:
    distance = float(dist)
  except ValueError:
    from Midas.midas_text import error
    error('%s: Invalid distance value %s' % (cmdname, dist))
    return

  multiscale_color_by_atoms(ms_models, atoms, distance)
    
# -----------------------------------------------------------------------------
# Command syntax: ~msc <multiscale-surface-id>
#
def multiscale_uncolor(cmdname, args):
    
  fields = args.split()

  if len(fields) != 1:
    from Midas.midas_text import error
    error('%s requires 1 argument, got %d: %s <multiscale-surface-id>'
          % (cmdname, len(fields), cmdname))
    return

  surf_spec = fields[0]

  ms_models = parse_multiscale_models(surf_spec, cmdname)
  if len(ms_models) == 0:
    return

  multiscale_uncolor_surfaces(ms_models)

# -----------------------------------------------------------------------------
#
def parse_multiscale_models(surf_spec, cmdname):
  
  # Parse multiscale models
  from chimera import specifier
  try:
    ssel = specifier.evalSpec(surf_spec)
  except:
    from Midas.midas_text import error
    error('%s: Bad model specifier %s' % (cmdname, surf_spec))
    return []

  ms_models = multiscale_models(ssel.models())

  if len(ms_models) == 0:
    from Midas.midas_text import error
    error('%s: No multiscale models specified by %s' % (cmdname, surf_spec))
    return []

  return ms_models

# -----------------------------------------------------------------------------
#
def parse_atom_specifier(atom_spec, cmdname):

  # Parse atoms
  from chimera import specifier
  try:
    asel = specifier.evalSpec(atom_spec)
  except:
    from Midas.midas_text import error
    error('%s: Bad atom specifier %s' % (cmdname, atom_spec))
    return []

  atoms = asel.atoms()
  if len(atoms) == 0:
    from Midas.midas_text import error
    error('%s: No atoms specified by specifier %s' % (cmdname, atom_spec))
    return []

  return atoms

# -----------------------------------------------------------------------------
#
def multiscale_color_by_atoms(ms_models, atoms, distance):

  pequiv = equivalent_surface_pieces(ms_models, atoms)

  import ColorZone
  point_colors = ColorZone.atom_colors(atoms)

  mpoints = {}
  plist = pequiv.keys()
  for p in plist:
    m = p.model
    if not m in mpoints:
      xform_to_surface = m.openState.xform
      xform_to_surface.invert()
      import SurfaceZone
      mpoints[m] = SurfaceZone.get_atom_coordinates(atoms, xform_to_surface)

  for p in plist:
    ColorZone.color_piece(p, mpoints[p.model], point_colors, distance)

  # Copy colors to equivalent chains.
  for p, pcopies in pequiv.items():
    for p2 in pcopies:
      if p2.surfacing_parameters == p.surfacing_parameters:
        p2.vertexColors = p.vertexColors
  
# -----------------------------------------------------------------------------
# Return a table whose keys are surface pieces part of the given multiscale
# models and associated with the given atoms and whose values are lists of
# equivalent surface pieces that do not have atoms in the given list.
#
def equivalent_surface_pieces(ms_models, atoms):

  # Make table of molecule chains.
  ctable = {}
  for atom in atoms:
    key = (atom.molecule, atom.residue.id.chainId)
    ctable[key] = 1

  # Get all multiscale chain pieces
  import MultiScale
  cplist = MultiScale.find_pieces(ms_models, MultiScale.Chain_Piece)

  # Find surface pieces of chain pieces with loaded atoms in the atom list.
  glist = []
  for cp in cplist:
    m = cp.molecule(load = False)
    cid = cp.lan_chain.chain_id
    key = (m, cid)
    if key in ctable:
      g = cp.surface_piece
      if g:
        glist.append(g)

  # Find surface pieces of equivalent chain pieces.
  gid = {}
  for g in glist:
    gid[g.model_piece.lan_chain.identifier()] = []
  for cp in cplist:
    id = cp.lan_chain.identifier()
    if id in gid:
      g = cp.surface_piece
      if g and not g in gid:
        gid[id].append(g)

  # Make table with pieces as keys instead of chain piece identifiers
  gequiv = {}
  for g in glist:
    gequiv[g] = gid[g.model_piece.lan_chain.identifier()]

  return gequiv
  
# -----------------------------------------------------------------------------
#
def multiscale_models(models):

  import MultiScale
  d = MultiScale.multiscale_model_dialog()
  if d == None:
    return []

  mlist = []
  for m in d.models:
    if m.surface_model(create = False):
      mlist.append(m)

  return mlist
  
# -----------------------------------------------------------------------------
#
def multiscale_uncolor_surfaces(ms_models):

  # Get all multiscale chain pieces
  import MultiScale
  cplist = MultiScale.find_pieces(ms_models, MultiScale.Chain_Piece)
  for cp in cplist:
    p = cp.surface_piece
    if p:
      p.vertexColors = None
