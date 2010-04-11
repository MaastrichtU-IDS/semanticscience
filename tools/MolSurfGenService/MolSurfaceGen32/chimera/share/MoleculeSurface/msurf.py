# -----------------------------------------------------------------------------
#
from _surface import SurfaceModel
class MSMSModel(SurfaceModel):

    def __init__(self, molecule, category, probeRadius = 1.4,
                 allComponents = True, vertexDensity = 2.0):

        SurfaceModel.__init__(self)

        name = 'MSMS %s surface of %s' % (category, molecule.name)
        SurfaceModel.__setattr__(self, 'name', name)
        SurfaceModel.__setattr__(self, 'piecesAreSelectable', True)
        SurfaceModel.__setattr__(self, 'oneTransparentLayer', True)

        init = {
            'molecule': molecule,
            'colorMode': self.ByAtom,
            'visibilityMode': self.ByAtom,
            'density': vertexDensity,
            'probeRadius': probeRadius,
            'category': category,
            'allComponents': allComponents,
            'atomMap': None,            # vertex number to Atom
            'surface_piece': None,
            'srf': None,                # MSMS surface object
            'triData': None,            # MSMS triangle data
            'areaSES': 0.0,
            'areaSAS': 0.0,
	    'calculationFailed': False,
            }
        self.__dict__.update(init)

        from _surface import SurfacePiece
        self.surface_piece_defaults = {
            'drawMode': self.Filled,
            'lineWidth': 1.0,
            'pointSize': 1.0,
            'useLighting': True,
            'twoSidedLighting': True,
            'smoothLines': False,
            'transparencyBlendMode': SurfacePiece.SRC_ALPHA_DST_1_MINUS_ALPHA,
            }

        self.update_surface()

        # Detect changes in atom color, atom surfaceColor, atom surfaceOpacity,
        #   molecule color, atom surfaceDisplay.
        from chimera import triggers as t
        self.molecule_handler = t.addHandler('Molecule', self.molecule_cb, None)

        # Detect when surface or molecule deleted.
        from chimera import addModelClosedCallback
        addModelClosedCallback(self, self.surface_closed_cb)
        addModelClosedCallback(self.molecule, self.molecule_closed_cb)

        import Surface
        Surface.set_coloring_method('msms', self, self.custom_coloring)
        Surface.set_visibility_method('msms', self, self.custom_visibility)

    # -------------------------------------------------------------------------
    # Draw mode values.
    #
    Filled = 0
    Mesh = 1
    Dot = 2

    # -------------------------------------------------------------------------
    # Color mode values
    #
    ByMolecule = 0
    ByAtom = 1
    Custom = 2

    # -------------------------------------------------------------------------
    # Change reasons.
    #
    DRAW_MODE_CHANGED = 'drawMode changed'
    LINE_WIDTH_CHANGED = 'lineWidth changed'
    POINT_SIZE_CHANGED = 'pointSize changed'
    USE_LIGHTING_CHANGED = 'useLighting changed'
    TWO_SIDED_LIGHTING_CHANGED = 'twoSidedLighting changed'
    SMOOTH_LINES_CHANGED = 'smoothLines changed'
    TRANSPARENCY_BLEND_MODE_CHANGED = 'transparencyBlendMode changed'
    COLOR_MODE_CHANGED = 'colorMode changed'
    VISIBILITY_MODE_CHANGED = 'visibilityMode changed'
    DENSITY_CHANGED = 'density changed'
    PROBE_RADIUS_CHANGED = 'probeRadius changed'
    CATEGORY_CHANGED = 'category changed'
    ALLCOMPONENTS_CHANGED = 'allComponents changed'
    CUSTOM_COLORS_CHANGED = 'customColors changed'
    CUSTOM_RGBA_CHANGED = 'customRGBA changed'

    # Need to hold references to reasons or crash occurs apparently because
    # TrackChanges is not incrementing the reason reference count.
    change_reason = {
        'drawMode': DRAW_MODE_CHANGED,
        'lineWidth': LINE_WIDTH_CHANGED,
        'pointSize': POINT_SIZE_CHANGED,
        'useLighting': USE_LIGHTING_CHANGED,
        'twoSidedLighting': TWO_SIDED_LIGHTING_CHANGED,
        'smoothLines': SMOOTH_LINES_CHANGED,
        'transparencyBlendMode': TRANSPARENCY_BLEND_MODE_CHANGED,
        'colorMode': COLOR_MODE_CHANGED,
        'visibilityMode': VISIBILITY_MODE_CHANGED,
        'density': DENSITY_CHANGED,
        'probeRadius': PROBE_RADIUS_CHANGED,
        'category': CATEGORY_CHANGED,
        'allComponents': ALLCOMPONENTS_CHANGED,
        'customColors': CUSTOM_COLORS_CHANGED,
        'customRGBA': CUSTOM_RGBA_CHANGED,
        }

    # -------------------------------------------------------------------------
    #
    def __setattr__(self, attrname, value):

        if attrname in ('drawMode', 'lineWidth', 'pointSize', 'useLighting',
                        'twoSidedLighting', 'smoothLines',
                        'transparencyBlendMode'):
            # SurfacePiece attributes
            if value == getattr(self, attrname):
                return
        elif attrname in ('colorMode', 'visibilityMode',
                          'density', 'probeRadius',
                          'category', 'allComponents'):
            if value == getattr(self, attrname):
                return
            self.__dict__[attrname] = value
        elif attrname not in ('customColors', 'customRGBA'):
            SurfaceModel.__setattr__(self, attrname, value)
            return

        if attrname in ('density', 'probeRadius', 'category', 'allComponents'):
            self.update_surface()
        else:
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return
            if attrname == 'drawMode':
                style = {self.Filled: p.Solid,
                         self.Mesh: p.Mesh,
                         self.Dot:  p.Dot,
                         }[value]
                p.displayStyle = style
            elif attrname == 'lineWidth':
                p.lineThickness = value
            elif attrname == 'pointSize':
                p.dotSize = value
            elif attrname in ('useLighting', 'twoSidedLighting', 'smoothLines',
                              'transparencyBlendMode'):
                setattr(p, attrname, value)
            elif attrname == 'colorMode':
                if value != self.Custom:
                    import Surface
                    Surface.set_coloring_method('msms', self,
                                                self.custom_coloring)
                    self.update_coloring()
            elif attrname == 'visibilityMode':
                if value == self.ByAtom:
                    import Surface
                    Surface.set_visibility_method('msms', self,
                                                  self.custom_visibility)
                    self.update_visibility()
            elif attrname == 'customColors':
                self.set_custom_colors(value)
            elif attrname == 'customRGBA':
                self.set_custom_rgba(value)

        self.report_change(self.change_reason[attrname])

    # -------------------------------------------------------------------------
    #
    def __getattr__(self, attrname):

        if attrname == 'customColors':
            vrgba = self.customRGBA
            if vrgba is None:
                return None
            from chimera import MaterialColor
            ccolors = [MaterialColor(*rgba) for rgba in vrgba]
            return ccolors
        elif attrname == 'customRGBA':
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return None
            vcolors = p.vertexColors
            return vcolors
        elif attrname == 'drawMode':
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return self.surface_piece_defaults[attrname]
            return {p.Solid: self.Filled,
                    p.Mesh: self.Mesh,
                    p.Dot: self.Dot}[p.displayStyle]
        elif attrname == 'lineWidth':
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return self.surface_piece_defaults[attrname]
            return p.lineThickness
        elif attrname == 'pointSize':
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return self.surface_piece_defaults[attrname]
            return p.dotSize
        elif attrname in ('useLighting', 'twoSidedLighting', 'smoothLines',
                          'transparencyBlendMode'):
            p = self.surface_piece
            if p is None or p.__destroyed__:
                return self.surface_piece_defaults[attrname]
            return getattr(p, attrname)
        elif attrname == 'atoms':
            return self.category_atoms(primary_atoms = False)
        elif attrname == 'bonds':
            return self.category_bonds(primary_atoms = False)
        elif attrname == 'vertexCount':
            if self.triData is None:
                return 0
            return len(self.triData[0])
        else:
            raise AttributeError, "MSMSModel has no attribute '%s'" % attrname

    # -------------------------------------------------------------------------
    # Called when an external coloring method is being used.
    #
    def custom_coloring(self, m):

        self.colorMode = self.Custom

    # -------------------------------------------------------------------------
    # Called when an external visibility method is being used.
    #
    def custom_visibility(self, m):

        self.visibilityMode = self.Custom

    # -------------------------------------------------------------------------
    # Generate TrackChanges event so dialogs such as selection inspector or
    # model inspector can update displayed surface parameter values.
    #
    def report_change(self, reason):

        from chimera import TrackChanges
        t = TrackChanges.get()
        t.addModified(self, reason)

    # -------------------------------------------------------------------------
    #
    def molecule_cb(self, trigger_name, closure, trigger_data):

        m = self.molecule
        if m and m in trigger_data.modified:
            r = trigger_data.reasons
            if 'surface major' in r or 'atoms moved' in r:
                self.update_surface()
            elif 'surface minor' in r:
                self.update_coloring()
                self.update_visibility()

    # -------------------------------------------------------------------------
    #
    def update_surface(self, set_visibility = True):

        if self.calculate_surface():
            self.update_coloring()
            if set_visibility:
                # When surface first created atom.surfaceDisplay = False
                self.update_visibility()

    # -------------------------------------------------------------------------
    #
    def calculate_surface(self):

        self.atomMap = None
        
        m = self.molecule
        if m is None:
            return False

        alist = self.category_atoms()
        from calcsurf import msms_geometry, Surface_Calculation_Error
	try:
            vfloat, vint, tri, atomareas, compareas, srf, allcomp = \
                msms_geometry(alist,
                              probe_radius = self.probeRadius,
                              vertex_density = self.density,
                              all_components = self.allComponents,
                              separate_process = True)
        except Surface_Calculation_Error, e:
            self.calculationFailed = True
            from chimera.replyobj import error
	    error(str(e) + '\n')
	    return False

        self.calculationFailed = False

        self.triData = (vfloat, vint, tri)
        self.srf = srf

        from numpy import array
        aa = array(alist)
        vatom = vint[:,1]
        self.atomMap = aa[vatom]

        varray = vfloat[:,:3]
        narray = vfloat[:,3:6]
        tarray = tri[:,:3]

        p = self.surface_piece
        if p is None or p.__destroyed__:
            self.surface_piece = p = self.newPiece()

        p.geometry = varray, tarray
        p.normals = narray

        # Set per-atom and per-residue surface areas
        if len(atomareas) == len(alist):
            for a, atom in enumerate(alist):
                ases, asas = [float(area) for area in atomareas[a]]
                atom.areaSES, atom.areaSAS = ases, asas
            for r in set([atom.residue for atom in alist]):
                r.areaSES = r.areaSAS = 0.0
            for a, atom in enumerate(alist):
                ases, asas = atomareas[a]
                r = atom.residue
                r.areaSES += ases
                r.areaSAS += asas
            self.areaSES = float(atomareas[:,0].sum())
            self.areaSAS = float(atomareas[:,1].sum())
            self.report_surface_areas(compareas)
        elif len(atomareas) > 0:
            from chimera.replyobj import warning
            warning('Incorrect number of atom areas reported.\n'
                    '%d areas reported for %d atoms'
                    % (len(atomareas), len(alist)))

        if allcomp != self.allComponents:
            self.__dict__['allComponents'] = allcomp
            self.report_change(self.change_reason['allComponents'])

        return True
    
    # -------------------------------------------------------------------------
    #
    def category_atoms(self, primary_atoms = True):

        m = self.molecule
        if m is None:
            return []

        if primary_atoms:
            atoms = m.primaryAtoms()
        else:
            atoms = m.atoms
        cat = self.category
        alist = [a for a in atoms if a.surfaceCategory == cat]
        return alist

    # -------------------------------------------------------------------------
    #
    def category_bonds(self, primary_atoms = True):

        m = self.molecule
        if m is None:
            return []
        bonds = bonds_between_atoms(m.bonds, self.category_atoms(primary_atoms))
        return bonds

    # -------------------------------------------------------------------------
    #
    def report_surface_areas(self, compareas):

        mname = self.molecule.name
        cname = self.category
        ncomp = len(compareas)
        lines = \
            ['',
             'Surface %s, category %s, probe radius %.4g, vertex density %.4g'
             % (mname, cname, self.probeRadius, self.density),
             '  %d connected surface components' % ncomp,
             '  Total solvent excluded surface area = %.6g' % self.areaSES]
        if ncomp > 1:
            careas = [(sesa, sasa) for sesa, sasa in compareas]
            careas.sort()
            careas.reverse()
            eareas = ', '.join(['%.6g' % sesa for sesa, sasa in careas])
            aareas = ', '.join(['%.6g' % sasa for sesa, sasa in careas])
            lines.append('    component areas = %s' % eareas)
        lines.append('  Total solvent accessible surface area = %.6g'
                     % self.areaSAS)
        if ncomp > 1:
            lines.append('    component areas = %s' % aareas)
        msg = '\n'.join(lines) + '\n'
        from chimera.replyobj import info, status
        info(msg)

        smsg = ('Surface %s, category %s has %d components'
                % (mname, cname, ncomp))
        status(smsg)

    # -------------------------------------------------------------------------
    #
    def update_coloring(self):

        p = self.surface_piece
        if p is None or p.__destroyed__:
            return

        cm = self.colorMode
        if cm == self.ByMolecule:
            m = self.molecule
            if m:
                rgba = molecule_surface_rgba(m)
                p.color = rgba
                p.vertexColors = None
        elif cm == self.ByAtom:
            m = self.molecule
            if m is None or self.atomMap is None:
                return
            mc = molecule_surface_rgba(m)
            rgba = [atom_surface_rgba(va, mc) for va in self.atomMap]
            if rgba:
                p.vertexColors = rgba

    # -------------------------------------------------------------------------
    #
    def set_custom_colors(self, vcolors):

        vrgba = [c.rgba() for c in vcolors]
        self.set_custom_rgba(vrgba)

    # -------------------------------------------------------------------------
    #
    def set_custom_rgba(self, vrgba):

        p = self.surface_piece
        if p is None or p.__destroyed__:
            return
        p.vertexColors = vrgba
        self.colorMode = self.Custom

    # -------------------------------------------------------------------------
    #
    def update_visibility(self):

        p = self.surface_piece
        if p is None or p.__destroyed__:
            return

        if self.visibilityMode == self.ByAtom:
            if self.atomMap is None:
                return      # Molecule has been closed.
            mask_bool = [va.surfaceDisplay for va in self.atomMap]
            from numpy import array, intc
            mask_int = array(mask_bool, intc)
            if mask_int.all():
                mask_int = None
            p.setTriangleMaskFromVertexMask(mask_int)

    # -------------------------------------------------------------------------
    #
    def surface(self):

        return self.srf

    # -------------------------------------------------------------------------
    #
    def	triangleData(self):

        return self.triData

    # -------------------------------------------------------------------------
    #
    def surface_closed_cb(self, s):

        self.remove_molecule_change_handler()
        for a in self.category_atoms():
            a.surfaceDisplay = False
            a.surfaceColor = None
        self.molecule = None

    # -------------------------------------------------------------------------
    #
    def molecule_closed_cb(self, s):

        self.molecule = None
        self.atomMap = None
        self.remove_molecule_change_handler()

    # -------------------------------------------------------------------------
    #
    def remove_molecule_change_handler(self):

        h = self.molecule_handler
        if h:
            from chimera import triggers as t
            t.deleteHandler('Molecule', h)
            self.molecule_handler = None

    # -------------------------------------------------------------------------
    # Note: MSMS sometimes uses 1 based array indices and other times
    # it uses 0 based array indices.  And it can change from release
    # to release.  The following two constants compensate for that.
    AtomOffset = 1
    VertexOffset = 0

# -----------------------------------------------------------------------------
#
def molecule_surface_rgba(m):

    c = m.surfaceColor or m.color
    rgba = c.rgba()
    o = m.surfaceOpacity
    if o >= 0:
        rgba = rgba[:3] + (o,)
    return rgba

# -----------------------------------------------------------------------------
#
def atom_surface_rgba(a, mrgba):

    c = a.surfaceColor or a.color
    if c:
        rgba = c.rgba()
    else:
        rgba = mrgba
    o = a.surfaceOpacity
    if o >= 0:
        rgba = rgba[:3] + (o,)
    return rgba

# -----------------------------------------------------------------------------
#
def bonds_between_atoms(bonds, atoms):

    blist = []
    aset = set(atoms)
    for b in bonds:
        if len([a for a in b.atoms if a not in aset]) == 0:
            blist.append(b)
    return blist

# -----------------------------------------------------------------------------
# Register MSMSModel change tracking at the C++ level.
#
from _chimera import TrackChanges
t = TrackChanges.get()
t.enroll(MSMSModel.__name__)
