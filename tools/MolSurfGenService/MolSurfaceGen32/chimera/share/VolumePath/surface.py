# -----------------------------------------------------------------------------
#
def make_marker_surface(mlist, surfmodel, caps):

  nt = marker_neighbors(mlist)
  cilist = connected_indices(nt)
  clist = []
  nc = []
  for ci in cilist:
    oc = order_chain(ci, nt)
    if oc is None:
      nc.extend(ci)
    else:
      clist.append(oc)
  if nc:
    raise No_Surface, ('branched chains not supported', [mlist[i] for i in nc])

  mxyz = [m.xyz() for m in mlist]
  from numpy import array, single as floatc
  varray = array(mxyz, floatc)

  from stitch import all_open_or_closed, order_chains
  if not all_open_or_closed(clist):
    raise No_Surface, ('some curves open ended others closed', [])
  oclist, axis = order_chains(clist, varray)
  from stitch import order_points_for_stitching, stitch_curves
  soclist = order_points_for_stitching(oclist, varray, axis)
  tarray = stitch_curves(soclist, varray, caps)
  if len(tarray) == 0:
    return None

  mrgba = [m.rgba() for m in mlist]
  colors = array(mrgba, floatc)
  multicolor = not (colors == colors[0]).all()
  if multicolor:
    rgba = (.7,.7,.7,1)
  else:
    rgba = colors[0]
    
  p = surfmodel.addPiece(varray, tarray, rgba)
  if multicolor:
    p.vertexColors = colors

  return p

# -----------------------------------------------------------------------------
# Return map of marker index to list of neighbor marker indices.
#
def marker_neighbors(mlist):

  mnum = {}
  for i,m in enumerate(mlist):
    mnum[m] = i
  nt = [[mnum[m2] for m2 in m.linked_markers() if m2 in mnum]
        for i,m in enumerate(mlist)]
  return nt

# -----------------------------------------------------------------------------
# Find connected indices given a list with each indices neighbors.
#
def connected_indices(nt):

  n = len(nt)
  ci = {}
  for i in range(n):
    ci[i] = [i]

  for i in range(n):
    ic = ci[i]
    for j in nt[i]:
      jc = ci.get(j, None)
      if jc and jc != ic:
        ic.extend(jc)
        for k in jc:
          ci[k] = ic

  c = [c for i,c in ci.items() if c[0] == i]
  return c

# -----------------------------------------------------------------------------
# Return indices in order to form a chain.  A table of neighbors for each
# index is given.  Chain can form closed loop or have two distinctend points.
# Neighbors not in input list are ignored.
#
def order_chain(ilist, nt):

  if len(ilist) == 0:
    return ilist

  iset = set(ilist)
  i = ilist[0]
  il = [j for j in nt[i] if j in iset]
  if len(il) == 0:
    c = [i]
  elif len(il) > 2:
    return None         # forked chain
  elif len(il) == 1:
    c = unbranched_chain(i, il[0], iset, nt)
  elif len(il) == 2:
    c = unbranched_chain(i, il[0], iset, nt)
    if c and c[-1] != i:
      c1 = unbranched_chain(i, il[1], iset, nt)[1:]
      if c1:
        c1.reverse()
        c = c1 + c
  if len(c) < len(ilist):
    return None         # multiple chains
  return c

# -----------------------------------------------------------------------------
#
def unbranched_chain(i1, i2, iset, nt):

  chain = [i1,i2]
  while True:
    il = [j for j in nt[i2] if j in iset]
    if len(il) == 2:
      if il[0] == i1: j = il[1]
      else: j = il[0]
      chain.append(j)
      if j == chain[0]:
        break           # Loop
      i1 = i2
      i2 = j
    elif len(il) == 1:
      break             # End point
    else:
      return None       # Forked

  return chain

# -----------------------------------------------------------------------------
# Trace chain of linked markers to other end.
#
def chain_end_marker(m):

  ml = m.linked_markers()
  if len(ml) != 1:
    return None         # Starting marker is not a chain end.
  m1 = m
  m2 = ml[0]
  while True:
    ml = m2.linked_markers()
    if len(ml) == 2:
      if ml[0] == m1:
        m1 = m2
        m2 = ml[1]
      else:
        m1 = m2
        m2 = ml[0]
    elif len(ml) == 1:
      return m2
    else:
      return None

# -----------------------------------------------------------------------------
# Topology problems.
#
class No_Surface(Warning):
  pass
