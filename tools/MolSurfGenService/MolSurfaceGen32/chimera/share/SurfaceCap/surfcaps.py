# -----------------------------------------------------------------------------
# Manager class for recalculating surface caps at clip planes as clip planes
# move or surface shape changes.
#
# Surfaces can be capped at multiple planes.  Each cap for a surface has a
# name (eg. 'per-model' or 'near').
#
class Surface_Capper:

    def __init__(self):

        self.cap_color = None                   # RGBA tuple or None
        self.mesh_style = False
        self.subdivision_factor = 1.0
        self.default_cap_offset = 0.01
        self.cap_offset = 0.01
        self.trigger_handlers = {
            ('Model', self.model_changed_cb): None,
            ('Camera', self.camera_changed_cb): None,
            ('OpenState', self.xform_changed_cb): None,
            ('SurfacePiece', self.surface_mask_changed_cb): None,
            }
        self.new_model_handler = None
        
    # -------------------------------------------------------------------------
    #
    def show_caps(self):

        for m in self.surface_models():
            self.show_cap(m)

        self.register_cap_handlers()

    # -------------------------------------------------------------------------
    #
    def show_cap(self, m):

        mc = model_capper(m)
        mc.show_caps(self.cap_offset, self.subdivision_factor,
                     self.mesh_style, self.cap_color)
            
    # -------------------------------------------------------------------------
    #
    def unshow_caps(self):

        self.deregister_cap_handlers()

        for m in self.surface_models():
            if not is_surface_deleted(m):
                self.unshow_cap(m)
        
    # -------------------------------------------------------------------------
    # The cap_name argument is 'per-model' or 'near' or None (implying both).
    #
    def unshow_cap(self, m, cap_name = None):

        mc = model_capper(m, create = False)
        if mc:
            mc.unshow_cap(cap_name)
        
    # -------------------------------------------------------------------------
    #
    def caps_shown(self):

        return not self.new_model_handler is None

    # -------------------------------------------------------------------------
    #
    def update_caps(self, surface_model_list):

        for m in surface_model_list:
            self.show_cap(m)
        
    # -------------------------------------------------------------------------
    #
    def set_cap_color(self, rgba):
        
        self.cap_color = rgba
        
    # -------------------------------------------------------------------------
    #
    def set_style(self, use_mesh):
        
        self.mesh_style = use_mesh
        
    # -------------------------------------------------------------------------
    #
    def set_subdivision_factor(self, sf):
        
        self.subdivision_factor = sf
        
    # -------------------------------------------------------------------------
    #
    def set_cap_offset(self, cap_offset):

        self.cap_offset = cap_offset
        
    # -------------------------------------------------------------------------
    #
    def surface_models(self):

        from _surface import SurfaceModel
        from chimera import openModels
        mlist = openModels.list(modelTypes = [SurfaceModel])
        return mlist

    # -------------------------------------------------------------------------
    #
    def register_cap_handlers(self):

        t = self.trigger_handlers
        for (name, callback), handler in t.items():
            if handler == None:
                import chimera
                h = chimera.triggers.addHandler(name, callback, None)
                t[(name, callback)] = h

        #
        # Using SurfacePiece trigger instead of geometry change callback
        # can lead to continuous updating when surface color auto-update is
        # also used.  Happens because trigger reasons are not associated
        # with specific objects.
        #
        for s in self.surface_models():
            s.addGeometryChangedCallback(self.geometry_changed_cb)

        from chimera import openModels as om
        self.new_model_handler = om.addAddHandler(self.new_model_cb, None)

    # -------------------------------------------------------------------------
    #
    def deregister_cap_handlers(self):

        t = self.trigger_handlers
        for (name, callback), handler in t.items():
            if handler:
                import chimera
                chimera.triggers.deleteHandler(name, handler)
                t[(name, callback)] = None

        for s in self.surface_models():
            s.removeGeometryChangedCallback(self.geometry_changed_cb)

        if self.new_model_handler:
            from chimera import openModels as om
            om.deleteAddHandler(self.new_model_handler)
            self.new_model_handler = None

    # -------------------------------------------------------------------------
    #
    def new_model_cb(self, trigName, unused, mlist):

        from _surface import SurfaceModel
        surfs = [m for m in mlist if isinstance(m, SurfaceModel)]
        for s in surfs:
            s.addGeometryChangedCallback(self.geometry_changed_cb)
        self.update_caps(surfs)

    # -------------------------------------------------------------------------
    # Capture per-model clip plane change.
    #
    def model_changed_cb(self, trigName, myData, trigData):

        r = trigData.reasons
        if ('useClipPlane changed' in r or
            'clipPlane changed' in r or
            'useClipThickness changed' in r or
            'clipThickness changed' in r):
            models = trigData.modified
            mlist = intersect_lists(models, self.surface_models())
            self.update_caps(mlist)
            
    # -------------------------------------------------------------------------
    #
    def geometry_changed_cb(self, p, type):

        if type == 'removed':
            # If surface piece deleted then remove its caps.
            if hasattr(p, 'name_to_cap_piece'):
                mc = model_capper(p.model)
                for cp in p.name_to_cap_piece.values():
                    mc.remove_cap_piece(cp)
        else:
            # Piece modified or added
            if not is_surface_cap(p):
                mc = model_capper(p.model)
                if mc:
                    mc.update_piece_caps(p)

    # -------------------------------------------------------------------------
    # Capture clip plane change.
    #
    def camera_changed_cb(self, trigName, myData, trigData):

        self.update_caps(self.surface_models())

    # -------------------------------------------------------------------------
    # Capture model motion.
    #
    def xform_changed_cb(self, trigName, myData, trigData):

        if 'transformation change' in trigData.reasons:
            from chimera import viewer
            if viewer.clipping:
                # TODO: Only need to update near clip plane cap.
                self.update_caps(self.surface_models())

    # -------------------------------------------------------------------------
    # Display mask for surface piece changed.
    #
    def surface_mask_changed_cb(self, trigName, myData, trigData):

        if 'display mask changed' in trigData.reasons:
            for p in trigData.modified:
                if not p.__destroyed__:
                    mc = model_capper(p.model)
                    if mc:
                        mc.update_piece_caps(p)

# -----------------------------------------------------------------------------
# Common cap calculation code for SurfaceModel.
#
class Model_Capper:

    def __init__(self, model):

        self.model = model
        
    # -------------------------------------------------------------------------
    #
    def show_caps(self, cap_offset, subdivision_factor, mesh_style, color):

        m = self.model
        planes = capped_clip_planes(m)
        for name, plane_normal, plane_offset in planes:
            if plane_normal:
                self.show_cap(name, plane_normal, plane_offset + cap_offset,
                              subdivision_factor, mesh_style, color)
            else:
                self.unshow_cap(name)
            
    # -------------------------------------------------------------------------
    # 
    def has_cap_geometry_changed(self, cap_piece, plane_normal, plane_offset,
                                 subdivision_factor):

        # TODO: Should ignore changes in plane due to limited float precision.
        return (cap_piece == None or
                cap_piece.cap_plane != (plane_normal, plane_offset) or
                cap_piece.cap_subdivision != subdivision_factor)
            
    # -------------------------------------------------------------------------
    # 
    def calculate_cap(self, varray, tarray,
                      plane_normal, plane_offset, subdivision_factor):

        # Clipping normals point in towards unclipped region.
        outward_normal = [-x for x in plane_normal]

        # TODO: Should warn about non-closed surfaces.
        import _surfacecap
        cvarray, ctarray = _surfacecap.compute_cap(outward_normal,
                                                   -plane_offset,
                                                   varray, tarray)
        if subdivision_factor > 0:
            cvarray, ctarray = _surfacecap.refine_mesh(cvarray, ctarray,
                                                       subdivision_factor)
        return cvarray, ctarray

    # -------------------------------------------------------------------------
    # Update cap color, style, normal orientation and display status.
    #
    def update_cap_properties(self, cp, displayed, mesh_style, color):

        if color:
            cp.color = color

        if mesh_style:
            style = cp.Mesh
        else:
            style = cp.Solid
        cp.displayStyle = style

        # Make cap display/undisplay state match parent display state.
        cp.display = displayed

# -----------------------------------------------------------------------------
#
class Surface_Model_Capper(Model_Capper):

    def __init__(self, surface_model):

        Model_Capper.__init__(self, surface_model)
        self.surface_model = surface_model

    # -------------------------------------------------------------------------
    #
    def show_cap(self, cap_name, plane_normal, plane_offset,
                 subdivision_factor, mesh_style, color):

        for p in self.surface_model.surfacePieces:
            # Don't cap the caps.
            if not is_surface_cap(p):
                self.cap_surface_piece(p, cap_name, plane_normal, plane_offset,
                                       subdivision_factor, mesh_style, color)

    # -------------------------------------------------------------------------
    # The cap_name argument is 'per-model' or 'near' or None (implying both).
    #
    def unshow_cap(self, cap_name):

        for cg in self.cap_pieces():
            if cap_name == None or cg.cap_name == cap_name:
                self.remove_cap_piece(cg)
    
    # -------------------------------------------------------------------------
    #
    def cap_model(self, create = True):

        return self.surface_model

    # -------------------------------------------------------------------------
    #
    def cap_piece(self, g, cap_name):

        if hasattr(g, 'name_to_cap_piece'):
            n2cg = g.name_to_cap_piece
            if cap_name in n2cg:
                return n2cg[cap_name]
        return None

    # -------------------------------------------------------------------------
    #
    def cap_pieces(self):

        cglist = []
        for p in self.surface_model.surfacePieces:
            if hasattr(p, 'name_to_cap_piece'):
                cglist.extend(p.name_to_cap_piece.values())
        return cglist

    # -------------------------------------------------------------------------
    #
    def remove_cap_piece(self, cap_piece):
                
        self.surface_model.removePiece(cap_piece)
        g = cap_piece.capped_surface
        del g.name_to_cap_piece[cap_piece.cap_name]
            
    # -------------------------------------------------------------------------
    #
    def cap_surface_piece(self, p, cap_name, plane_normal, plane_offset,
                          subdivision_factor, mesh_style, color):

        cp = self.cap_piece(p, cap_name)
        if self.has_cap_geometry_changed(cp, plane_normal, plane_offset,
                                         subdivision_factor):
            cp = self.update_cap_geometry(p, cap_name,
                                          plane_normal, plane_offset,
                                          subdivision_factor)
        if cp:
            self.update_cap_properties(cp, p.display, mesh_style,
                                       color or p.color)
            
    # -------------------------------------------------------------------------
    #
    def update_piece_caps(self, g):

        if hasattr(g, 'name_to_cap_piece'):
            for cap_name, cg in g.name_to_cap_piece.items():
                plane_normal, plane_offset = cg.cap_plane
                self.update_cap_geometry(g, cap_name,
                                         plane_normal, plane_offset,
                                         cg.cap_subdivision)

    # -------------------------------------------------------------------------
    #
    def update_cap_geometry(self, g, cap_name, plane_normal, plane_offset,
                            subdivision_factor):

        if hasattr(g, 'outline_box'):
            return None         # Volume outline boxes don't get capped.

        varray, tarray = g.maskedGeometry(g.Solid)
        cvarray, ctarray = self.calculate_cap(varray, tarray,
                                              plane_normal, plane_offset,
                                              subdivision_factor)
        cg = self.cap_piece(g, cap_name)
        if cg == None:
            cg = self.surface_model.newPiece()
            cg.cap_name = cap_name
            cg.capped_surface = g
            if not hasattr(g, 'name_to_cap_piece'):
                g.name_to_cap_piece = {}
            g.name_to_cap_piece[cap_name] = cg
            # Need to first set cap attributes before updating geometry
            # so geometry changed callbacks can see this piece is a cap.
            cg.geometry = cvarray, ctarray
        else:
            cg.geometry = cvarray, ctarray
            
        cg.cap_plane = (plane_normal, plane_offset)
        cg.cap_subdivision = subdivision_factor

#        print 'updated cap' , cg, ' for', g
#        from traceback import print_stack
#        print_stack()
        return cg

# -----------------------------------------------------------------------------
# Return the cap manager for a given model.
#
def model_capper(model, create = True):

    if not hasattr(model, 'caps'):
        if create:
            import _surface
            if isinstance(model, _surface.SurfaceModel):
                model.caps = Surface_Model_Capper(model)
        else:
            return None
    return model.caps
    
# -----------------------------------------------------------------------------
# Return SurfaceModel used for caps of given model.
#
def cap_model(model, create = True):

    mc = model_capper(model, create)
    if mc == None:
        cm = None
    else:
        cm = mc.cap_model(create)
    return cm
        
# -----------------------------------------------------------------------------
# Test if a SurfacePiece is a cap.
#
def is_surface_cap(s):

    return hasattr(s, 'capped_surface')

# -----------------------------------------------------------------------------
# Return a list of (name, plane_normal, plane_offset).
# The plane_normal and plane_offset values can be None indicating the named
# clip plane is turned off.
#
def capped_clip_planes(model):

    planes = []

    pm_plane_normal, pm_plane_offset = per_model_clip_plane(model)
    planes.append(('per-model', pm_plane_normal, pm_plane_offset))

    pmb_plane_normal, pmb_plane_offset = per_model_back_clip_plane(model)
    planes.append(('per-model-back', pmb_plane_normal, pmb_plane_offset))

    near_plane_normal, near_plane_offset = \
                       near_clip_plane(model.openState.xform)
    planes.append(('near', near_plane_normal, near_plane_offset))

    return planes

# -----------------------------------------------------------------------------
# Returned plane is in untransformed model coordinates.
# Normal points towards unclipped half-space.
#
def near_clip_plane(model_xform):

    from chimera import viewer, Vector
    if not viewer.clipping:
        return None, None
    xf = model_xform
    neg_z = Vector(0,0,-1)
    xf.invert()
    n = xf.apply(neg_z)
    near, far = viewer.camera.nearFar
    t = xf.getTranslation()
    plane_offset = -near + t*n
    plane_normal = n.data()
    return plane_normal, plane_offset

# -----------------------------------------------------------------------------
# Returned plane is in untransformed model coordinates.
# Normal points towards unclipped half-space.
#
def per_model_clip_plane(model):
    
    if not model.useClipPlane:
        return None, None
    p = model.clipPlane
    plane_normal = p.normal.data()
    plane_offset = -p.offset()
    return plane_normal, plane_offset

# -----------------------------------------------------------------------------
# Returned plane is in untransformed model coordinates.
# Normal points towards unclipped half-space.
#
def per_model_back_clip_plane(model):
    
    if (not model.useClipPlane or
        not model.useClipThickness or
        model.clipThickness <= 0):
        return None, None
    p = model.clipPlane
    plane_normal = map(lambda x: -x, p.normal.data())
    plane_offset = p.offset() - model.clipThickness
    return plane_normal, plane_offset

# -----------------------------------------------------------------------------
# Test if a SurfaceModel, SurfacePiece is deleted.
#
def is_surface_deleted(s):

    return s.__destroyed__

# -----------------------------------------------------------------------------
#
def intersect_lists(list1, list2):

    t = {}
    for e in list2:
        t[e] = 1
    both = filter(lambda e: t.has_key(e), list1)
    return both

# -----------------------------------------------------------------------------
#
the_capper = None
def capper():

    global the_capper
    if the_capper is None:
        the_capper = Surface_Capper()
    return the_capper

# -----------------------------------------------------------------------------
#
def enable_capping(enable):

    c = capper()
    if enable:
        c.show_caps()
    else:
        c.unshow_caps()
