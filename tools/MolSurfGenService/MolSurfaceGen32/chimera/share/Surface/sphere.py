# ------------------------------------------------------------------------------
# Compute an approximate bounding sphere in world coordinates for a list of
# surface pieces.  Include only the unmasked vertices.
#
def surface_sphere(plist):

  bs = None
  for p in plist:
    s = surface_piece_sphere(p)
    if s:
      if bs is None: bs = s
      else: bs.merge(s)
  return bs

# ------------------------------------------------------------------------------
# Compute an approximate bounding sphere in world coordinates for a
# surface piece including only the unmasked vertices.
#
def surface_piece_sphere(p):

  has_box, box = p.bbox()
  if not has_box:
    return None
  cl = box.center()
  c = p.model.openState.xform.apply(cl)
  bsize = (box.urb - box.llf).data()
  r = 0.5 * max(bsize)
  from chimera import Sphere
  s = Sphere()
  s.center = c
  s.radius = r
  return s
