# -----------------------------------------------------------------------------
# Show only part of the surface model within specified distances of the given
# list of points.  The points are in model coordinates.
#
def hide_dust(model, method, limit, auto_update):

    plist = model.surfacePieces
    for p in plist:
        hide_dust_piece(p, method, limit)
    if auto_update:
        dust_updater.auto_dust(model, method, limit)

# -----------------------------------------------------------------------------
#
def hide_dust_piece(p, method, limit):

# TODO: Caps should not appear on hidden blobs.
#    import SurfaceCap
#    if SurfaceCap.is_surface_cap(p):
#        return

    b = getattr(p, 'blobs', None)
    if b is None or p.triangleCount != b.triangle_count:
        b = Blob_Masker(p)
        p.blobs = b
    m = b.triangle_mask(method, limit)
    set_triangle_mask(p, m)
    p.hiding_dust = True
        
# -----------------------------------------------------------------------------
# Stop updating dust hiding.
#
def unhide_dust(model):
    
    dust_updater.stop_hiding_dust(model)

# -----------------------------------------------------------------------------
#
class Blob_Masker:

    def __init__(self, p):

        self.varray, self.tarray = p.geometry
        self.triangle_count = len(self.tarray)

        self.blist = None
        self.tbindex = None
        self.tbsizes = None
        self.tbranks = None
        self.tbvolumes = None
        self.tmask = None

    def triangle_mask(self, method, limit):

        mask = self.mask_array()
        from numpy import greater
        if method == 'size':
            greater(self.blob_sizes(), limit, mask)
        elif method == 'rank':
            r = len(self.blob_list()) - int(limit+1)
            greater(self.blob_ranks(), r, mask)
        elif method == 'volume':
            greater(self.blob_volumes(), limit, mask)
        return mask

    def triangle_blob_indices(self):
        if self.tbindex is None:
            from numpy import empty, intc
            tbi = empty((self.triangle_count,), intc)
            for i, (vi, ti) in enumerate(self.blob_list()):
                tbi.put(ti, i)
            self.tbindex = tbi
        return self.tbindex

    def blob_sizes(self):
        if self.tbsizes is None:
            bsizes = self.blob_values(self.blob_size)
            self.tbsizes = bsizes[self.triangle_blob_indices()]
        return self.tbsizes

    def blob_size(self, vi, ti):
        v = self.varray[vi,:]
        return max(v.max(axis=0) - v.min(axis=0))

    def blob_ranks(self):
        if self.tbranks is None:
            border = self.blob_values(self.blob_size).argsort()
            branks = border.copy()
            from numpy import arange
            branks.put(border, arange(len(border)))
            self.tbranks = branks[self.triangle_blob_indices()]
        return self.tbranks

    def blob_volumes(self):
        if self.tbvolumes is None:
            bvolumes = self.blob_values(self.blob_volume)
            self.tbvolumes = bvolumes[self.triangle_blob_indices()]
        return self.tbvolumes

    def blob_volume(self, vi, ti):
        from MeasureVolume import enclosed_volume
        t = self.tarray[ti,:]
        vol, holes = enclosed_volume(self.varray, t)
        if vol is None:
            vol = 0
        return vol

    def blob_values(self, value_func):
        blist = self.blob_list()
        from numpy import empty, single as floatc
        bv = empty((len(blist),), floatc)
        for i, (vi,ti) in enumerate(blist):
            bv[i] = value_func(vi, ti)
        return bv

    def blob_list(self):
        if self.blist is None:
            from _surface import connected_pieces
            self.blist = connected_pieces(self.tarray)
        return self.blist

    def mask_array(self):
        if self.tmask is None:
            from numpy  import empty, intc
            self.tmask = empty((self.triangle_count,), intc)
        return self.tmask
            
# -----------------------------------------------------------------------------
#
class Dust_Updater:

    def __init__(self):

        self.models = {}

        import SimpleSession
        import chimera
        chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
                                    self.save_session_cb, None)
            
    # -------------------------------------------------------------------------
    #
    def auto_dust(self, model, method, limit):

        add_callback = not self.models.has_key(model)
        self.models[model] = (method, limit)
        from Surface import set_visibility_method
        set_visibility_method('hide dust', model, self.stop_hiding_dust)
        if add_callback:
            model.addGeometryChangedCallback(self.surface_changed_cb)
            import chimera
            chimera.addModelClosedCallback(model, self.model_closed_cb)
            
    # -------------------------------------------------------------------------
    #
    def stop_hiding_dust(self, model):

        if model in self.models:
            del self.models[model]
            model.removeGeometryChangedCallback(self.surface_changed_cb)
            # Redisplay full surfaces
            plist = model.surfacePieces
            for p in plist:
                if hasattr(p, 'hiding_dust') and p.hiding_dust:
                    show_all_triangles(p)
                    p.hiding_dust = False
                    p.blobs = None
            
    # -------------------------------------------------------------------------
    #
    def surface_changed_cb(self, p, detail):

        if detail == 'removed':
            return

        m = p.model
        (method, limit) = self.models[m]
        hide_dust_piece(p, method, limit)
            
    # -------------------------------------------------------------------------
    #
    def model_closed_cb(self, model):

        if model in self.models:
            del self.models[model]
    
    # -------------------------------------------------------------------------
    #
    def save_session_cb(self, trigger, x, file):

        import session
        session.save_hide_dust_state(self.models, file)

# -----------------------------------------------------------------------------
# TODO: Make set_triangle_mask() surface piece method.
#
def set_triangle_mask(p, m):

    mask = p.triangleAndEdgeMask
    if mask is None:
        mask = m * 0xf
    else:
        mask &= 0x7
        mask |= (m * 0x8)
    p.triangleAndEdgeMask = mask

# -----------------------------------------------------------------------------
#
def show_all_triangles(p):

    mask = p.triangleAndEdgeMask
    if not mask is None:
        mask |= 0x8
        p.triangleAndEdgeMask = mask

# -----------------------------------------------------------------------------
#
def hiding_dust(model):
    return model in dust_updater.models
def dust_limit(model):
    return dust_updater.models[model]

# -----------------------------------------------------------------------------
#
dust_updater = Dust_Updater()
