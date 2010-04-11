# -----------------------------------------------------------------------------
#
class Selection_Mover:

    # Movement modes.
    NORMAL_MOVEMENT = 'move normal'
    MOVE_SELECTION = 'move selection'
    MOVE_CHAIN = 'move chain'
    MOVE_MOLECULE = 'move molecule'
    MOVE_SECONDARY_STRUCTURE = 'move secondary structure'

    def __init__(self):

        self.previous_xy = None
        self.movable_groups = []
        self.rotation_center = None

        self.history = []
        self.history_location = 0           # For handling undo / redo
        self.history_merge_interval = 1.0   # seconds
        self.history_limit = 100            # Number of states remembered
        
        self.mode = self.NORMAL_MOVEMENT
        
        self.move_callbacks = {
            'rotate':{'down': self.rotate_mouse_down_cb,
                      'drag': self.rotate_mouse_drag_cb,
                      'up': self.mouse_up_cb},
            'translate x,y':{'down': self.translate_mouse_down_cb,
                      'drag': self.translate_xy_mouse_drag_cb,
                      'up': self.mouse_up_cb},
            'translate z':{'down': self.translate_mouse_down_cb,
                      'drag': self.translate_z_mouse_drag_cb,
                      'up': self.mouse_up_cb}
            }
        
        self.original_move_callbacks = self.wrap_mouse_modes()

    # -------------------------------------------------------------------------
    #
    def wrap_mouse_modes(self):

        from chimera.mousemodes import addFunction, functionCallables

        mt = {}
        for mode in ('rotate', 'translate x,y', 'translate z'):
            down_cb, drag_cb, up_cb = functionCallables(mode)
            mt[mode] = {'down':down_cb, 'drag':drag_cb, 'up':up_cb}

        m = self.mouse_cb
        for mode in ('rotate', 'translate x,y', 'translate z'):
            callbacks = (lambda v,e,mode=mode: m(v,e,mode,'down'),
                         lambda v,e,mode=mode: m(v,e,mode,'drag'),
                         lambda v,e,mode=mode: m(v,e,mode,'up'))
            addFunction(mode, callbacks)

        return mt
    
    # -------------------------------------------------------------------------
    #
    def mouse_cb(self, viewer, event, mode_name, action):

        if self.mode == self.NORMAL_MOVEMENT:
            self.original_move_callbacks[mode_name][action](viewer, event)
        else:
            if action == 'down':
                self.record_movable_objects(event)
            if self.nothing_movable():
                # Normal motion if nothing is movable.
                self.original_move_callbacks[mode_name][action](viewer, event)
                return
            self.move_callbacks[mode_name][action](viewer, event)

    # -------------------------------------------------------------------------
    #
    def rotate_mouse_down_cb(self, viewer, event):

        viewer.recordPosition(event.time, event.x, event.y, "rotate")
        self.rotation_center = center_of_rotation(self.movable_groups)
    
    # -------------------------------------------------------------------------
    #
    def translate_mouse_down_cb(self, viewer, event):

        self.rotation_center = center_of_rotation(self.movable_groups)
        self.previous_xy = (event.x, event.y)
  
    # -------------------------------------------------------------------------
    #
    def mouse_up_cb(self, viewer, event):

        viewer.setCursor(None)
        
    # -------------------------------------------------------------------------
    #
    def rotate_mouse_drag_cb(self, viewer, event):

        # Get rotation about origin.
	xf = viewer.vsphere(event.time, event.x, event.y, event.state % 2 == 1)

        cx, cy, cz = self.rotation_center
        
        # Change center of rotation to act about center of movable objects.
        from chimera import Xform
        xf.multiply(Xform.translation(-cx, -cy, -cz))
        xf.premultiply(Xform.translation(cx, cy, cz))

        self.move_objects(xf)
    
    # -------------------------------------------------------------------------
    #
    def translate_xy_mouse_drag_cb(self, viewer, event):

        px, py = self.previous_xy
        dx = event.x - px
        dy = event.y - py
        self.previous_xy = (event.x, event.y)
        psize = pixel_size_at_rotation_center(self.rotation_center)

        if event.state & 0x1:
            psize *= 0.1        # Slow motion when shift key held

        from chimera import Xform
        xf = Xform.translation(psize*dx, -psize*dy, 0)

        self.move_objects(xf)

        # Translate fixed rotation center.
        from chimera import openModels
        if openModels.cofrMethod == openModels.Fixed:
            openModels.cofr = xf.apply(openModels.cofr)
    
    # -------------------------------------------------------------------------
    #
    def translate_z_mouse_drag_cb(self, viewer, event):

        px, py = self.previous_xy
        dx = event.x - px
        dy = event.y - py
        self.previous_xy = (event.x, event.y)
        psize = pixel_size_at_rotation_center(self.rotation_center)

        if event.state & 0x1:
            psize *= 0.1        # Slow motion when shift key held

        if abs(dy) > abs(dx):
            dz = dy
        else:
            dz = dx
        
        import chimera
        xf = chimera.Xform.translation(0, 0, psize*dz)

        self.move_objects(xf)

        # Translate fixed rotation center.
        from chimera import openModels
        if openModels.cofrMethod == openModels.Fixed:
            openModels.cofr = xf.apply(openModels.cofr)

    # -------------------------------------------------------------------------
    #
    def record_movable_objects(self, event):

        mode = self.mode
        if mode == self.MOVE_SELECTION:
            from chimera import selection
            atoms = selection.currentAtoms()
            chains = selected_multiscale_chains()
            spieces = selected_surface_pieces()
            self.movable_groups = objects_grouped_by_model(atoms, chains,
                                                           spieces)
        elif mode in (self.MOVE_MOLECULE, self.MOVE_CHAIN,
                      self.MOVE_SECONDARY_STRUCTURE):
            from chimera import viewer, Atom, Residue
            # TODO: Appears to be a bug where picking 1a0m ribbon gives
            # lists of many erroneous residues.  It is caused by LensViewer
            # pick(x,y) doing drag pick using previously set x,y!  Not clear
            # why since there is separate dragPick(x,y) method.
            viewer.delta(event.x, event.y) # Sets lastx, lasty
            objects = viewer.pick(event.x, event.y)
            atoms = [a for a in objects if isinstance(a, Atom)]
            residues = [r for r in objects if isinstance(r, Residue)]
            if mode == self.MOVE_MOLECULE:
                catoms = extend_to_molecules(atoms, residues)
                mschains = multiscale_chain_pieces(objects,
                                                   full_molecules = True)
            elif mode == self.MOVE_CHAIN:
                catoms = extend_to_chains(atoms, residues)
                mschains = multiscale_chain_pieces(objects)
            elif mode == self.MOVE_SECONDARY_STRUCTURE:
                catoms = extend_to_secondary_structure(atoms, residues)
                mschains = []
            self.movable_groups = objects_grouped_by_model(catoms, mschains)
        else:
            self.movable_groups = []

    # -------------------------------------------------------------------------
    #
    def nothing_movable(self):

        return len(self.movable_groups) == 0

    # -------------------------------------------------------------------------
    #
    def move_objects(self, xf):

        for g in self.movable_groups:
            g.move_objects(g.global_to_local_xform(xf))
        self.record_move(self.movable_groups, xf)

    # -------------------------------------------------------------------------
    #
    def record_move(self, groups, xf):

        import time
        t = time.time()
        h = self.history
        hloc = self.history_location

        # Remember local transforms for each group.
        lxf = [g.global_to_local_xform(xf) for g in groups]
        
        # Combine moves of the same objects made in rapid succession.
        hprev = hloc - 1
        if hprev >= 0 and hprev < len(h):
            pgroups, plxf, pt = h[hprev]
            if groups == pgroups and t - pt <= self.history_merge_interval:
                for k in range(len(groups)):
                    plxf[k].premultiply(lxf[k])
                h[hprev][2] = t
                return

        # Add new state to the history
        h.insert(hloc, [groups, lxf, t])
        self.history_location = hloc + 1

        self.trim_history()

    # -------------------------------------------------------------------------
    # Remove states if history length is greater than limit.
    #
    def trim_history(self):

        h = self.history
        while len(h) > self.history_limit:
            hloc = self.history_location
            if hloc > self.history_limit - hloc:
                del h[0]
                self.history_location = hloc - 1
            else:
                del h[-1]

    # -------------------------------------------------------------------------
    #
    def undo_move(self):

        h = self.history
        hloc = self.history_location
        hprev = hloc - 1
        if hprev >= 0 and hprev < len(h):
            pgroups, plxf, pt = h[hprev]
            for k in range(len(pgroups)):
                pgroups[k].move_objects(plxf[k].inverse())
            self.history_location = hprev
            return True
        return False

    # -------------------------------------------------------------------------
    #
    def redo_move(self):

        h = self.history
        hloc = self.history_location
        if hloc >= 0 and hloc < len(h):
            ngroups, nlxf, nt = h[hloc]
            for k in range(len(ngroups)):
                ngroups[k].move_objects(nlxf[k])
            self.history_location = hloc + 1
            return True
        return False

# -----------------------------------------------------------------------------
#
def pixel_size_at_rotation_center(rotation_center):

    from chimera import viewer as v
    c = v.camera
    pixel_size = 2*c.focalExtent / v.windowSize[0]  # at focal plane
    if c.ortho:
        return pixel_size

    rc = rotation_center
    if rc is None:
        rc = v.camera.center.data()
    zc = rc[2]
    zeye = c.eyePos(0)[2]           # view 0
    fdist = zeye - c.focal
    cdist = zeye - zc
    if fdist != 0 :
        pixel_size *= cdist / fdist
    return pixel_size

# -----------------------------------------------------------------------------
#
def atoms_by_model(atoms):

    agroups = group_items(atoms, lambda a: a.molecule)
    ma = [Molecule_Atoms(alist) for alist in agroups]
    return ma

# -----------------------------------------------------------------------------
#
def group_items(objects, id):

    ot = {}
    for o in objects:
        i = id(o)
        if not i in ot:
            ot[i] = [o]
        else:
            ot[i].append(o)
    og = ot.values()
    return og
    
# -----------------------------------------------------------------------------
#
def selected_multiscale_chains():

    import MultiScale
    d = MultiScale.multiscale_model_dialog()
    if d:
        chains = d.selected_chains(selected_surfaces_only = True,
                                   warn_if_none_selected = False)
    else:
        chains = []
    return chains

# -----------------------------------------------------------------------------
#
def multiscale_chain_pieces(objects, full_molecules = False):

    from _surface import SurfacePiece
    sg = [c for c in objects if isinstance(c, SurfacePiece)]
    from MultiScale import containing_chain_pieces
    mschains = set(containing_chain_pieces(sg))
    if full_molecules:
        lm = set([p.lan_chain.lan_molecule for p in mschains])
        par = [p.parent for p in mschains if not p.parent is None]
        for p in par:
            for c in p.children:
                if c.lan_chain.lan_molecule in lm:
                    mschains.add(c)
    return list(mschains)

# -----------------------------------------------------------------------------
#
def multiscale_chains_by_model(chains):

    cgroups = group_items(chains, lambda c: c.surface_model())
    mc = [Multiscale_Chains(clist) for clist in cgroups]
    return mc

# -----------------------------------------------------------------------------
#
def selected_surface_pieces():

    from Surface import selected_surface_pieces
    from MultiScale import is_chain_piece
    spieces = [p for p in selected_surface_pieces() if not is_chain_piece(p)]
    return spieces

# -----------------------------------------------------------------------------
#
def surface_pieces_by_model(spieces):

    pgroups = group_items(spieces, lambda p: p.model)
    mp = [Surface_Pieces(plist) for plist in pgroups]
    return mp

# -----------------------------------------------------------------------------
#
def objects_grouped_by_model(atoms, multiscale_chains = [],
                             surface_pieces = []):

    groups = (atoms_by_model(atoms) +
              multiscale_chains_by_model(multiscale_chains) +
              surface_pieces_by_model(surface_pieces))
    return groups
        
# -------------------------------------------------------------------------
#
def center_of_rotation(object_groups):

    from chimera import openModels
    m = openModels.cofrMethod
    if m == openModels.Fixed or m == openModels.CenterOfView:
        return openModels.cofr.data()

    points = [g.local_to_global_coordinates(g.center()) for g in object_groups]

    return center_of_points(points)

# -----------------------------------------------------------------------------
# Set of selectable objects from a single model.
#
class Model_Objects:

    def model(self):

        return None     # Must override this method.
        
    def model_xform(self):

        return self.model().openState.xform
            
    def global_to_local_xform(self, xf):

        gxf = self.model_xform()
        lxf = gxf.inverse()
        lxf.multiply(xf)
        lxf.multiply(gxf)
        return lxf
            
    def local_to_global_coordinates(self, xyz):

        import chimera
        gxyz = self.model_xform().apply(chimera.Point(*xyz)).data()
        return gxyz

# -----------------------------------------------------------------------------
# Set of atoms from a single molecule.
#
class Molecule_Atoms(Model_Objects):

    def __init__(self, atoms):

        self.atoms = atoms

    def __eq__(self, ma):

        return isinstance(ma, Molecule_Atoms) and ma.atoms == self.atoms
    
    def move_objects(self, xf):

        for a in self.atoms:
            if not a.__destroyed__:
                a.setCoord(xf.apply(a.coord()))

    def model(self):

        if self.atoms:
            return self.atoms[0].molecule
        return None

    def center(self):

        points = [a.coord().data() for a in self.atoms]
        return center_of_points(points)

# -----------------------------------------------------------------------------
# Set of chain pieces from a single multiscale model.
#
class Multiscale_Chains(Model_Objects):

    def __init__(self, chains):

        self.chains = chains

    def __eq__(self, mc):

        return isinstance(mc, Multiscale_Chains) and mc.chains == self.chains

    def move_objects(self, xf):

        for c in self.chains:
            if not c.lan_chain is None:
                c.move_piece(xf)
            
    def model(self):

        if self.chains:
            return self.chains[0].surface_model()
        return None

    def center(self):

        spheres = [c.surface_piece.bsphere() for c in self.chains]
        centers = [s.center.data() for have,s in spheres if have]
        return center_of_points(centers)

# -----------------------------------------------------------------------------
# Set of surface pieces from a single surface model.
#
class Surface_Pieces(Model_Objects):

    def __init__(self, pieces):

        self.pieces = pieces

    def __eq__(self, mp):

        return isinstance(mp, Surface_Pieces) and mp.pieces == self.pieces

    def move_objects(self, xf):

        from Matrix import xform_matrix
        tf = xform_matrix(xf)
        from _contour import affine_transform_vertices
        for p in self.pieces:
            varray, tarray = p.geometry
            affine_transform_vertices(varray, tf)
            p.geometry = varray, tarray
            
    def model(self):

        if self.pieces:
            return self.pieces[0].model
        return None

    def center(self):

        spheres = [p.bsphere() for p in self.pieces]
        centers = [s.center.data() for have,s in spheres if have]
        return center_of_points(centers)

# -----------------------------------------------------------------------------
#
def extend_to_molecules(atoms, residues):

    mset = set([a.molecule for a in atoms])
    mset.update([r.molecule for r in residues])
    atoms = []
    for m in mset:
        atoms.extend(m.atoms)
    return atoms

# -----------------------------------------------------------------------------
#
def extend_to_chains(atoms, residues):

    cset = set([(a.molecule, a.residue.id.chainId) for a in atoms])
    cset.update(set([(r.molecule, r.id.chainId) for r in residues]))

    # Map molecules to set of chains.
    mt = dict([(m,set()) for m,c in cset])
    for m,c in cset:
        mt[m].add(c)

    # Find all atoms in chains
    catoms = []
    for m, c in cset:
        catoms.extend([a for a in m.atoms if a.residue.id.chainId in c])

    return catoms

# -----------------------------------------------------------------------------
#
def extend_to_secondary_structure(atoms, residues):

    # Extend only protein chains.
    atoms = [a for a in atoms if 'CA' in a.residue.atomsMap]
    residues = [r for r in residues if 'CA' in r.atomsMap]

    rt = {}
    for a in atoms:
        rt[a.residue] = 1
    for r in residues:
        rt[r] = 0
    rlist = rt.keys()

    mt = {}
    for r in rlist:
        mt[r.molecule] = 1

    rmap = {}
    mlist = mt.keys()
    for m in mlist:
        for r in m.residues:
            if 'CA' in r.atomsMap:
                # Only extend along protein chains.
                rmap[(m,r.id.chainId,r.id.position)] = r

    for r in rlist:
        m = r.molecule
        pos = r.id.position
        cid = r.id.chainId
        sec = (r.isHelix, r.isStrand, r.isTurn)
        p = pos + 1
        while (m,cid,p) in rmap:
            r2 = rmap[(m,cid,p)]
            if (not r2 in rt and
                (r2.isHelix, r2.isStrand, r2.isTurn) == sec):
                p += 1
                rt[r2] = 1
            else:
                break
        p = pos - 1
        while (m,cid,p) in rmap:
            r2 = rmap[(m,cid,p)]
            if (not r2 in rt and
                (r2.isHelix, r2.isStrand, r2.isTurn) == sec):
                p -= 1
                rt[r2] = 1
            else:
                break

    alist = []
    for r in rt.keys():
        alist.extend(r.atoms)

    return alist

# -----------------------------------------------------------------------------
#
def center_of_points(points):

    import chimera
    plist = map(lambda xyz: chimera.Point(*xyz), points)
    valid, sphere = chimera.find_bounding_sphere(plist)
    if not valid:
        return None
    c = sphere.center.data()
    return c
    
# -----------------------------------------------------------------------------
# TODO: GUI dialog does not update to reflect new mode.
#
def toggle_move_selection_mouse_modes():

    m = mover(create = True)
    if m.mode == Selection_Mover.MOVE_SELECTION:
        m.mode = Selection_Mover.NORMAL_MOVEMENT
    elif m.mode == Selection_Mover.NORMAL_MOVEMENT:
        m.mode = Selection_Mover.MOVE_SELECTION
    
# -----------------------------------------------------------------------------
#
def set_mouse_mode(mode):

    m = mover(create = True)
    if m:
        m.mode = mode

# -----------------------------------------------------------------------------
#
def undo_move():

    m = mover()
    if m and not m.undo_move():
        from chimera import replyobj
        replyobj.status('No move to undo')

# -----------------------------------------------------------------------------
#
def redo_move():

    m = mover()
    if m and not m.redo_move():
        from chimera import replyobj
        replyobj.status('No move to redo')

# -----------------------------------------------------------------------------
#
the_mover = None
def mover(create = False):

    global the_mover
    if create and the_mover == None:
        the_mover = Selection_Mover()
    return the_mover
