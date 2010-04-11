# -----------------------------------------------------------------------------
# Color surfaces near specified points.
#
from zones import split_volume_by_color_zone

# -----------------------------------------------------------------------------
# Color the surface model within specified distances of the given
# list of points using the corresponding point colors.
# The points are in model object coordinates.
#
def color_zone(model, points, point_colors, distance, auto_update):

    if auto_update:
        zone_updater.auto_zone(model, points, point_colors, distance)
    
    plist = model.surfacePieces
    for p in plist:
        color_piece(p, points, point_colors, distance)

# -----------------------------------------------------------------------------
#
def points_and_colors(atoms, bonds, xform_to_surface,
                      bond_point_spacing = None):

    import SurfaceZone
    points = SurfaceZone.get_atom_coordinates(atoms, xform_to_surface)
    colors = atom_colors(atoms)

    from SurfaceZone.bondzone import bond_points_and_colors, concatenate_points
    bpoints, bcolors = bond_points_and_colors(bonds, xform_to_surface,
                                              bond_point_spacing)
    if not bpoints is None:
        points = concatenate_points(points, bpoints)
        colors.extend(bcolors)

    return points, colors

# -----------------------------------------------------------------------------
#
def atom_colors(atoms):

    rgba_list = map(atom_rgba, atoms)
    return rgba_list

# -----------------------------------------------------------------------------
#
def atom_rgba(atom):

    c = atom.color
    if c == None:
        c = atom.molecule.color
    rgba = c.rgba()
    return rgba

# -----------------------------------------------------------------------------
#
def color_piece(p, points, point_colors, distance):

    varray, tarray = p.geometry

    from _closepoints import find_closest_points, BOXES_METHOD
    i1, i2, n1 = find_closest_points(BOXES_METHOD, varray, points, distance)

    from VolumeData import allocate_array
    from numpy import single as floatc
    rgba = allocate_array((len(varray),4), floatc, reverse_indices = False)
    rgba[:,:] = p.color
    for k in range(len(i1)):
        rgba[i1[k],:] = point_colors[n1[k]]
        
    p.vertexColors = rgba
    p.coloring_zone = True

# -----------------------------------------------------------------------------
#
def is_surface_piece_deleted(g):

    try:
        g.display
    except:
        return True
    return False
        
# -----------------------------------------------------------------------------
# Stop updating surface zone.
#
def uncolor_zone(model):
    
    zone_updater.stop_zone(model)
            
# -----------------------------------------------------------------------------
#
class Zone_Updater:

    def __init__(self):

        self.models = {}

        import SimpleSession
        import chimera
        chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
                                    self.save_session_cb, None)
            
    # -------------------------------------------------------------------------
    #
    def auto_zone(self, model, points, colors, distance):

        add_callback = not self.models.has_key(model)
        self.models[model] = (points, colors, distance)
        from Surface import set_coloring_method
        set_coloring_method('color zone', model, self.stop_zone)
        if add_callback:
            model.addGeometryChangedCallback(self.surface_changed_cb)
            import chimera
            chimera.addModelClosedCallback(model, self.model_closed_cb)
            
    # -------------------------------------------------------------------------
    #
    def stop_zone(self, model):

        if model in self.models:
            del self.models[model]
            model.removeGeometryChangedCallback(self.surface_changed_cb)
            # Redisplay single color
            plist = model.surfacePieces
            for p in plist:
                if hasattr(p, 'coloring_zone') and p.coloring_zone:
                    p.vertexColors = None
                    p.coloring_zone = False
            
    # -------------------------------------------------------------------------
    #
    def surface_changed_cb(self, p, detail):

        if detail == 'removed':
            return
        m = p.model
        (points, point_colors, distance) = self.models[m]
        color_piece(p, points, point_colors, distance)
            
    # -------------------------------------------------------------------------
    #
    def model_closed_cb(self, model):

        if model in self.models:
            del self.models[model]
    
    # -------------------------------------------------------------------------
    #
    def save_session_cb(self, trigger, x, file):

        import session
        session.save_color_zone_state(self.models, file)

# -----------------------------------------------------------------------------
#
def zonable_surface_models():

  import chimera
  import _surface
  mlist = chimera.openModels.list(modelTypes = [_surface.SurfaceModel])
  import SurfaceCap
  mlist = filter(lambda m: not SurfaceCap.is_surface_cap(m), mlist)

  return mlist

# -----------------------------------------------------------------------------
#
def coloring_zone(model):
    return model in zone_updater.models
def zone_points_colors_and_distance(model):
    return zone_updater.models[model]

# -----------------------------------------------------------------------------
#
zone_updater = Zone_Updater()
