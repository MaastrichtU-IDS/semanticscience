# -----------------------------------------------------------------------------
#
def surface_models():

  from chimera import openModels as om
  from _surface import SurfaceModel
  mlist = om.list(modelTypes = [SurfaceModel])
  return mlist

# -----------------------------------------------------------------------------
#
def selected_surface_pieces(sel = None, include_outline_boxes = True):

  if sel is None:
    from chimera import selection
    sel = selection._currentSelection

  from _surface import SurfacePiece, SurfaceModel
  ps = set()
  for p in sel.vertices():
    if isinstance(p, SurfacePiece):
      ps.add(p)
  for s in sel.barrenGraphs():
    if isinstance(s, SurfaceModel):
      for p in s.surfacePieces:
        ps.add(p)
  plist = list(ps)

  if not include_outline_boxes:
    plist = [p for p in plist if not hasattr(p, 'outline_box')]

  return plist

# -----------------------------------------------------------------------------
#
def surface_pieces(slist, include_outline_boxes = False,
                   include_surface_caps = False):

  plist = []
  from SurfaceCap import is_surface_cap
  for s in slist:
    for p in s.surfacePieces:
      if ((include_surface_caps or not is_surface_cap(p)) and
          (include_outline_boxes or not hasattr(p, 'outline_box'))):
        plist.append(p)
  return plist

# -----------------------------------------------------------------------------
#
def all_surface_pieces(include_outline_boxes = True):

  from _surface import SurfacePiece, SurfaceModel
  from chimera import openModels as om
  slist = om.list(modelTypes = [SurfaceModel])
  plist = []
  if include_outline_boxes:
    for s in slist:
      plist.extend(s.surfacePieces)
  else:
    for s in slist:
      plist.extend([p for p in s.surfacePieces
                    if not hasattr(p, 'outline_box')])
  return plist

# -----------------------------------------------------------------------------
# Toggle whether volume and multiscale surfaces are selectable with the mouse.
#
def toggle_surface_selectability():
  from _surface import SurfaceModel
  from chimera import openModels as om
  for m in om.list(modelTypes = [SurfaceModel]):
    m.piecesAreSelectable = not m.piecesAreSelectable

# -----------------------------------------------------------------------------
#
def color_surfaces(plist):
  'Show color dialog to color selected items'
  if plist:
    cw = color_surface_color_well()
    cw.plist = plist
    cw.deactivate()
    cw.showColor(plist[0].color)
    cw.activate()

# -----------------------------------------------------------------------------
#
cscw = None
def color_surface_color_well():
  global cscw
  if cscw == None:
    from CGLtk.color.ColorWell import ColorWell
    from chimera.tkgui import app
    cscw = ColorWell(app, callback = color_surface_cb)
  return cscw

# -----------------------------------------------------------------------------
#
def color_surface_cb(rgba):
  if len(rgba) == 4:
    cw = color_surface_color_well()
    for p in cw.plist:
      p.color = rgba
      p.vertexColors = None        # Turn off per-vertex coloring

# -----------------------------------------------------------------------------
#
def show_surfaces_as_mesh(plist):
  for p in plist:
    p.displayStyle = p.Mesh

# -----------------------------------------------------------------------------
#
def show_surfaces_filled(plist):
  for p in plist:
    p.displayStyle = p.Solid

# -----------------------------------------------------------------------------
#
def show_surfaces(plist):
  for p in plist:
    p.display = True

# -----------------------------------------------------------------------------
#
def hide_surfaces(plist):
  for p in plist:
    p.display = False

# -----------------------------------------------------------------------------
#
def delete_surfaces(plist):
  for p in plist:
    p.model.removePiece(p)

# -----------------------------------------------------------------------------
#
def split_selected_surfaces():

  plist = selected_surface_pieces()
  if plist:
    pplist = split_surfaces(plist)
    from chimera.replyobj import status
    status('%d surface pieces' % len(pplist))

# -----------------------------------------------------------------------------
#
def split_surfaces(plist):

  pplist = []
  for p in plist:
    pieces = split_surface_piece(p)
    pplist.extend(pieces)
    if pieces:
      # Select pieces if original surface selected.
      from chimera.selection import containedInCurrent
      if containedInCurrent(p):
        from chimera.selection import addCurrent, removeCurrent
        removeCurrent(p)  # Get error missing C++ object without this.
        p.model.removePiece(p)
        addCurrent(pieces)
  return pplist

# -----------------------------------------------------------------------------
#
def split_surface_piece(p):

  varray, tarray = p.geometry
  from _surface import connected_pieces
  cplist = connected_pieces(tarray)
  if len(cplist) > 1:
    pplist = copy_surface_piece_blobs(p, varray, tarray, cplist)
    return pplist
  return []

# -----------------------------------------------------------------------------
#
def copy_surface_piece_blobs(p, varray, tarray, cplist):

  from numpy import zeros, int32
  vmap = zeros(len(varray), int32)

  pplist = []
  m = p.model
  narray = p.normals
  color = p.color
  vrgba = p.vertexColors
  temask = p.triangleAndEdgeMask
  for pi, (vi,ti) in enumerate(cplist):
    pp = copy_piece_blob(m, varray, tarray, narray, color, vrgba, temask,
                         vi, ti, vmap)
    copy_piece_attributes(p, pp)
    pp.oslName = p.oslName + (' %d' % (pi+1))
    pplist.append(pp)

  return pplist

# -----------------------------------------------------------------------------
#
def copy_piece_blob(m, varray, tarray, narray, color, vrgba, temask,
                     vi, ti, vmap):

  va = varray.take(vi, axis = 0)
  ta = tarray.take(ti, axis = 0)

  # Remap triangle vertex indices for shorter vertex list.
  from numpy import arange
  vmap[vi] = arange(len(vi), dtype = vmap.dtype)
  ta = vmap.take(ta.ravel()).reshape((len(ti),3))

  gp = m.addPiece(va, ta, color)

  na = narray.take(vi, axis = 0)
  gp.normals = na

  if not vrgba is None:
    gp.vertexColors = vrgba.take(vi, axis = 0)
  if not temask is None:
    gp.triangleAndEdgeMask = temask.take(ti, axis = 0)

  return gp

# -----------------------------------------------------------------------------
#
def copy_piece_attributes(g, gp):

  gp.display = g.display
  gp.displayStyle = g.displayStyle
  gp.useLighting = g.useLighting
  gp.twoSidedLighting = g.twoSidedLighting
  gp.lineThickness = g.lineThickness
  gp.smoothLines = g.smoothLines
  gp.transparencyBlendMode = g.transparencyBlendMode
  gp.oslName = g.oslName
