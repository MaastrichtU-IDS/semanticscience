# -----------------------------------------------------------------------------
# Per-model clipping Chimera command mclip.
#
# mclip #1-3            # Model specifier can be "all".
#       axis 0,0,1      # Can also be "x", "y", or "z".
#       origin 3.2,1,5  # Can also be "center" (of bounding box).
#       coords local    # Can be "local" or "screen".
#       offset 5.0
#       stagger 0.1     # Make non-coincident planes for multiple models.
#       match #0        # Match clip plane of a specified model.
#                       #   Can also be "focalplane", "near", or "nearfar".
#       flip false      # Flip plane 180 degrees.
#       slab false
#       thickness 10.0  # Slab thickness.
#
# Only specified clipping parameters are changed, while unspecified ones
# remain at their current values.  If a model has not been clipped before
# and the axis is not specified it defaults to "z", and if origin has not been
# specified it defaults to "center".  The offset is not a remembered parameter
# -- it alters the origin which is remembed.  The match option overrides other
# options except for offset, stagger and flip.  Specifying no arguments
# turns on clipping for all models.
#
# ~mclip #2-4           # Turn off per-model clipping.
#       
def mclip_command(cmdname, args):

    if len(args) == 0:
        args = 'all'
    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(mclip, args)

# -----------------------------------------------------------------------------
#
def unclip_command(cmdname, args):

    if len(args) == 0:
        from chimera import openModels as om
        unclip_models(om.list())
    else:
        from Midas.midas_text import doExtensionFunc
        doExtensionFunc(unclip_models, args)

# -----------------------------------------------------------------------------
#
def mclip(models, axis = None, origin = None, coords = 'local',
          offset = 0.0, stagger = 0.0, match = None, flip = False,
          slab = None, thickness = None):

    from Midas import MidasError

    mlist = parse_model_spec(models)
    if len(mlist) == 0:
        raise MidasError, 'No models specified by "%s"' % str(models)

    csys = ('local', 'screen')
    for c in csys:
        if c.startswith(coords): coords = c
    if not coords in csys:
        raise MidasError, ('coords must be %s, got "%s"' %
                           (' or '.join(csys), str(coords)))

    axes = {'x':(1,0,0), 'y':(0,1,0), 'z':(0,0,1)}
    if axis in axes:
        axis = axes[axis]
    elif not axis is None and axis != 'current':
        axis = parse_floats(axis, 'axis', 3)

    if not origin is None and origin != 'center':
        origin = parse_floats(origin, 'origin', 3)

    for name in ('offset', 'stagger', 'thickness'):
        val = locals()[name]
        if not val is None and not isinstance(val, (float,int)):
            raise MidasError, '%s must be number, got "%s"' % (name, str(val))

    for name in ('flip', 'slab'):
        val = locals()[name]
        if not val is None and not isinstance(val, (bool,int)):
            raise MidasError, ('%s must be true/false, got "%s"'
                               % (name, str(val)))

    axis, origin, coords, slab, thickness = \
        match_settings(match, axis, origin, coords, slab, thickness)

    clip_models(mlist, axis, origin, coords,
                offset, stagger, flip, slab, thickness)

# -----------------------------------------------------------------------------
#
def match_settings(match, axis, origin, coord, slab, thickness):

    if match in ('near', 'nearfar', 'focal'):
        coord = 'screen'
        axis = (0,0,1)
        from chimera import viewer
        c = viewer.camera
        origin = c.center        # Focal plane center point
        near,far = c.nearFar
        if match != 'focal':
            origin = apply_offset(origin, axis, near-c.focal)
        if match == 'nearfar':
            slab = True
            thickness = near-far
    elif not match is None:
        mlist = parse_model_spec(match)
        if len(mlist) != 1:
            from Midas import MidasError
            raise MidasError, 'match value must be a model id or "near", "nearfar" or "focal", got "%s"' % str(match)
        m = mlist[0]
        p = m.clipPlane
        xf = m.openState.xform
        axis = xf.apply(-p.normal).data()
        origin = xf.apply(p.origin).data()
        coord = 'screen'
        slab = m.useClipThickness
        thickness = m.clipThickness

    return axis, origin, coord, slab, thickness

# -----------------------------------------------------------------------------
#
def clip_models(models, axis, origin, coord,
                offset, stagger, flip, slab, thickness):

    if origin == 'center' or origin is None:
        screen_origin = center_of_models(models)
    elif coord == 'screen':
        screen_origin = origin
    else:
        screen_origin = None

    for m in models:
        default_plane = (tuple(m.clipPlane.normal.data()) == (0,0,0))

        if origin is None and not default_plane:
            o = None
        elif screen_origin:
            xfinv = m.openState.xform.inverse()
            from chimera import Point
            o = xfinv.apply(Point(*screen_origin)).data()
        else:
            o = origin

        if axis is None:
            if default_plane:
                a = (0,0,1)
            else:
                a = None
        elif coord == 'screen':
            xfinv = m.openState.xform.inverse()
            from chimera import Vector
            a = xfinv.apply(Vector(*axis)).data()
        else:
            a = axis

        clip_model(m, a, o, offset, slab, thickness, flip)

        if not stagger is None:
            offset += stagger

# -----------------------------------------------------------------------------
#
def clip_model(m, axis, origin, offset, slab, thickness, flip):

    if origin is None:
        origin = m.clipPlane.origin.data()
    if axis is None:
        axis = (-m.clipPlane.normal).data()
        
    if flip:
        axis = tuple([-x for x in axis])

    if offset != 0:
        origin = apply_offset(origin, axis, offset)
    from chimera import Plane, Point, Vector
    p = Plane()
    p.origin = Point(*origin)
    p.normal = -Vector(*axis)
    m.clipPlane = p
    if not slab is None:
        m.useClipThickness = slab
    if not thickness is None:
        m.clipThickness = thickness
    m.useClipPlane = True

# -----------------------------------------------------------------------------
#
def unclip_models(models):        

    if isinstance(models, str):
        mlist = parse_model_spec(models)
        if len(mlist) == 0:
           from Midas import MidasError     
           raise MidasError, 'No models specified by "%s"' % str(models)
    else:
        mlist = models

    for m in mlist:
        m.useClipPlane = False

# -----------------------------------------------------------------------------
# Screen coordinates.
# Transform each model box to coordinates of first box to compute center.
# Transforming boxes to screen coordinates is not as good as the result
# depends on the overall rotation.
#
def center_of_models(models):

    box = None
    for m in models:
        has_box, b = m.bbox()
        if has_box:
            xf = m.openState.xform
            if box is None:
                box = b
                bxf = xf
            else:
                xf.premultiply(bxf.inverse())
                b.xform(xf)
                box.merge(b)
    if box:
        c = bxf.apply(box.center()).data()
    else:
        c = (0,0,0)
    return c

# -----------------------------------------------------------------------------
#
def apply_offset(origin, axis, offset):

    return tuple([origin[a] + offset * axis[a] for a in range(3)])

# -----------------------------------------------------------------------------
#
def parse_model_spec(mspec):

    if mspec.lower() == 'all':
        from chimera import openModels as om
        mlist = om.list()
    else:
        from chimera.specifier import evalSpec
        try:
            mlist = evalSpec(mspec).models()
        except:
            mlist = []
    return mlist

# -----------------------------------------------------------------------------
#
def parse_floats(value, name, count, default = None):

    if value is None:
        return default
    try:
        v = [float(c) for c in value.split(',')]
    except:
        v = []
    if not len(v) == count:
        from Midas import MidasError
        raise MidasError, ('%s value must be %d comma-separated numbers, got %s'
                           % (name, count, str(value)))
    return v
