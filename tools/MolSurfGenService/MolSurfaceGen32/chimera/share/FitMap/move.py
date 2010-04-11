# -----------------------------------------------------------------------------
# Remember model and atom positions relative to a given model.
#
class Position_History:

    def __init__(self):

        self.cur_position = -1
        self.positions = []
        self.max_positions = 100

    def record_position(self, models, atoms, base_model):

        plist = self.positions
        c = self.cur_position
        if c < len(plist)-1:
            del plist[c+1:]      # Erase redo states.
        ps = position_state(models, atoms, base_model)
        self.positions.append(ps)
        if len(plist) > self.max_positions:
            del plist[0]
        else:
            self.cur_position += 1

    def undo(self):

        while self.can_undo():
            ps = self.positions[self.cur_position]
            self.cur_position -= 1
            if restore_position(ps):
                return True
        return False

    def can_undo(self):
        return self.cur_position >= 0

    def redo(self):

        while self.can_redo():
            self.cur_position += 1
            ps = self.positions[self.cur_position]
            if restore_position(ps):
                return True
        return False

    def can_redo(self):
        return self.cur_position+1 < len(self.positions)

# -----------------------------------------------------------------------------
#
def position_state(models, atoms, base_model):

  bos = base_model.openState
  bxfinv = bos.xform.inverse()
  osset = set([m.openState for m in models])
  osset.update(set([a.molecule.openState for a in atoms]))
  oslist = []
  for os in osset:
      xf = os.xform
      xf.premultiply(bxfinv)
      oslist.append((os, xf))
  apos = [(a,a.coord()) for a in atoms]
  return (bos, oslist, apos)

# -----------------------------------------------------------------------------
#
def restore_position(pstate, angle_tolerance = 1e-5, shift_tolerance = 1e-5):

    bos, oslist, apos = pstate
    if bos.__destroyed__:
        return False
    changed = False
    from Matrix import same_xform
    for os, xf in oslist:
        if os.__destroyed__:
            continue
        oxf = bos.xform
        oxf.multiply(xf)
        if not same_xform(os.xform, oxf, angle_tolerance, shift_tolerance):
            changed = True
        os.xform = oxf

    for a,c in apos:
        if a.__destroyed__:
            continue
        if a.coord() != c:
            changed = True
        a.setCoord(c)
    return changed

# -----------------------------------------------------------------------------
#
def move_models_and_atoms(tf, models, atoms, move_whole_molecules, base_model):

    if move_whole_molecules:
        models = list(models) + list(set([a.molecule for a in atoms]))
        atoms = []
    global position_history
    position_history.record_position(models, atoms, base_model)
    import Matrix
    xf = Matrix.chimera_xform(tf)
    for os in set([m.openState for m in models]):
        os.globalXform(xf)
    for a in atoms:
        mxfinv = a.molecule.openState.xform.inverse()
        a.setCoord(mxfinv.apply(xf.apply(a.xformCoord())))
    position_history.record_position(models, atoms, base_model)

# -----------------------------------------------------------------------------
#
position_history = Position_History()
