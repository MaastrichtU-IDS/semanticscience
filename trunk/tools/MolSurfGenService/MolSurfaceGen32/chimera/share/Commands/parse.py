# -----------------------------------------------------------------------------
#
from Midas import MidasError as CommandError

# -----------------------------------------------------------------------------
#
def parse_arguments(cmd_name, arg_string,
                    required_args = (), optional_args = (), keyword_args = ()):

    # TODO: Handle quoting of arguments
    fields = arg_string.split()
    n = len(fields)
    akw = {}
    a = 0

    # Parse required arguments.
    for spec in required_args:
        if a >= n:
            raise CommandError, ('%s: Missing required argument "%s"'
                                 % (cmd_name, arg_specifier_name(spec)))
        parse_arg(fields[a], spec, cmd_name, akw)
        a += 1

    # Make keyword abbreviation table.
    kw_args = tuple(optional_args) + tuple(keyword_args)
    kwnames = [arg_specifier_name(s) for s in kw_args]
    kwt = abbreviation_table(kwnames)

    # Parse optional arguments.
    for spec in optional_args:
        if a >= n or fields[a].lower() in kwt:
            break
        parse_arg(fields[a], spec, cmd_name, akw)
        a += 1

    # Parse keyword arguments.
    keyword_spec = dict([(arg_specifier_name(s),s) for s in kw_args])
    while a < n:
        f = fields[a]
        fl = f.lower()
        if not fl in kwt:
            raise CommandError, '%s: Unknown keyword "%s"' % (cmd_name, f)
        if a+1 >= n:
            raise CommandError, '%s: Missing argument for keyword "%s"' % (cmd_name, f)
        parse_arg(fields[a+1], keyword_spec[kwt[fl]], cmd_name, akw)
        a += 2
        
    return akw

# -----------------------------------------------------------------------------
#
def parse_arg(arg, spec, cmd_name, akw):

    name, parse, pkw = arg_spec(spec)
    try:
        akw[name] = parse(arg, **pkw)
    except CommandError, e:
        raise CommandError, ('%s invalid %s argument "%s": %s'
                             % (cmd_name, name, arg, str(e)))
    except:
        raise CommandError, ('%s invalid %s argument "%s"'
                             % (cmd_name, name, arg))

# -----------------------------------------------------------------------------
# Return argument name, parsing function, parsing function keyword dictionary.
# Original specifiers can be just a name or tuple of name and parse func.
#
def arg_spec(s):

    if isinstance(s, basestring):
        s3 = (s, string_arg, {})
    elif len(s) == 1:
        s3 = (s[0], string_arg, {})
    elif len(s) == 2:
        s3 = (s[0], s[1], {})
    elif len(s) == 3:
        s3 = tuple(s)
    return s3

# -----------------------------------------------------------------------------
#
def arg_specifier_name(s):

    if isinstance(s, basestring):
        return s
    return s[0]

# -----------------------------------------------------------------------------
#
def string_arg(s):

    return s

# -----------------------------------------------------------------------------
#
def bool_arg(s):

    return s.lower() not in ('false', 'f', '0', 'no', 'n', 'off')

# -----------------------------------------------------------------------------
#
def float_arg(s):

    return float(s)

# -----------------------------------------------------------------------------
#
def molecule_arg(s):

    from chimera.specifier import evalSpec
    sel = evalSpec(s)
    mlist = sel.molecules()
    if len(mlist) == 0:
        raise CommandError, 'No molecule specified'
    elif len(mlist) > 1:
        raise CommandError, 'Multiple molecules specified'
    return mlist[0]

# -----------------------------------------------------------------------------
#
def molecules_arg(s):

    from chimera.specifier import evalSpec
    sel = evalSpec(s)
    mlist = sel.molecules()
    return mlist

# -----------------------------------------------------------------------------
#
def model_arg(s):

    from chimera.specifier import evalSpec
    sel = evalSpec(s)
    mlist = sel.models()
    if len(mlist) == 0:
        raise CommandError, 'No models specified'
    elif len(mlist) > 1:
        raise CommandError, 'Multiple models specified'
    return mlist[0]

# -----------------------------------------------------------------------------
#
def filter_volumes(models, keyword = ''):

    if keyword:
        keyword += ' '
        
    if isinstance(models, str):
        raise CommandError, 'No %svolumes specified by "%s"' % (keyword, models)
    
    from VolumeViewer import Volume
    from _volume import Volume_Model
    vids = set([v.id for v in models if isinstance(v, (Volume, Volume_Model))])
    for v in models:
        if not isinstance(v, (Volume, Volume_Model)) and not v.id in vids:
            raise CommandError, 'Model %s is not a volume' % v.name
    volumes = [v for v in models if isinstance(v, Volume)]
    if len(volumes) == 0:
        raise CommandError, 'No %svolumes specified' % keyword
    return volumes

# -----------------------------------------------------------------------------
#
def parse_floats(value, name, count, default = None):

    return parse_values(value, float, name, count, default)

# -----------------------------------------------------------------------------
#
def parse_ints(value, name, count, default = None):

    return parse_values(value, int, name, count, default)

# -----------------------------------------------------------------------------
#
def parse_values(value, vtype, name, count, default = None):

    if isinstance(value, (tuple, list)):
        vlist = value
    elif isinstance(value, basestring):
        vlist = value.split(',')
    elif value is None:
        return default
    else:
        vlist = []
    try:
        v = [vtype(c) for c in vlist]
    except:
        v = []
    if not len(v) == count:
        raise CommandError, ('%s value must be %d comma-separated numbers, got %s'
                           % (name, count, str(value)))
    return v

# -----------------------------------------------------------------------------
# Case insenstive and converts unique prefix to full string.
#
def parse_enumeration(string, strings, default = None):

    ast = abbreviation_table(strings)
    s = ast.get(string.lower(), default)
    return s

# -----------------------------------------------------------------------------
# Return table mapping unique abbreviations for names to the full name.
#
def abbreviation_table(names, lowercase = True):

    a = {}
    for name in names:
        for i in range(1,len(name)):
            aname = name[:i]
            if lowercase:
                aname = aname.lower()
            if aname in a:
                a[aname] = None
            else:
                a[aname] = name
    # Delete duplicate abbreviations
    for n,v in a.items():
        if v is None:
            del a[n]
    # Make sure name is in table even if it is abbrev of some other name.
    for name in names:
        if lowercase:
            aname = name.lower()
        else:
            aname = name
        a[aname] = name
    return a

# -----------------------------------------------------------------------------
#
def parse_model_id(modelId):

    if modelId is None:
        from chimera import openModels as om
        return (om.Default, om.Default)
    mid = None
    if isinstance(modelId, basestring):
        if modelId and modelId[0] == '#':
            modelId = modelId[1:]
        try:
            mid = tuple([int(i) for i in modelId.split('.')])
        except ValueError:
            mid = None
        if len(mid) == 1:
            mid = (mid[0], 0)
        elif len(mid) != 2:
            mid = None
    elif isinstance(modelId, int):
        mid = (modelId, 0)
    if mid is None:
        raise CommandError, 'modelId must be integer, got "%s"' % str(modelId)
    return mid

# -----------------------------------------------------------------------------
#
def parse_step(value, name = 'step', require_3_tuple = False):

    if isinstance(value, int):
        step = value
    else:
        try:
            step = parse_values(value, int, name, 3, None)
        except CommandError:
            step = parse_values(value, int, name, 1, None)[0]
    if require_3_tuple and isinstance(step, int):
        step = (step, step, step)
    return step

# -----------------------------------------------------------------------------
#
def parse_subregion(value, name = 'subregion'):

    if value.count(',') == 0:
        r = value       # Named region.
    else:
        s6 = parse_values(value, int, name, 6, None)
        r = (s6[:3], s6[3:])
    return r

# -----------------------------------------------------------------------------
#
def parse_rgba(color):

    from chimera import MaterialColor
    if isinstance(color, MaterialColor):
        rgba = color.rgba()
    elif isinstance(color, (tuple,list)):
        rgba = color
    else:
        raise CommandError, 'Unknown color "%s"' % str(color)
    return rgba

# -----------------------------------------------------------------------------
#
def check_number(value, name, type = (float,int), allow_none = False,
                 positive = False, nonnegative = False):

    if allow_none and value is None:
        return
    if not isinstance(value, type):
        raise CommandError, '%s must be number, got "%s"' % (name, str(value))
    if positive and value <= 0:
        raise CommandError, '%s must be > 0' % name
    if nonnegative and value < 0:
        raise CommandError, '%s must be >= 0' % name

# -----------------------------------------------------------------------------
#
def check_in_place(inPlace, volumes):

    if not inPlace:
        return
    nwv = [v for v in volumes if not v.data.writable]
    if nwv:
        names = ', '.join([v.name for v in nwv])
        raise CommandError, "Can't modify volume in place: %s" % names

# -----------------------------------------------------------------------------
#
def check_matching_sizes(v1, v2, step, subregion, operation):

    if v1.data.size != v2.data.size:
        raise CommandError, 'Cannot %s grids of different size' % operation
    if step or subregion:
        if not v1.same_region(v1.region, v2.region):
            raise CommandError, 'Cannot %s grids with different subregions' % operation

# -----------------------------------------------------------------------------
#
def parse_surfaces(surfaces):
    
    from _surface import SurfaceModel
    surfs = set([s for s in surfaces if isinstance(s, SurfaceModel)])
    if len(surfs) == 0:
        raise CommandError, 'No surfaces specified'
    return surfs

# -----------------------------------------------------------------------------
#
def parse_surface_pieces(spec):

    from chimera.specifier import evalSpec
    sel = evalSpec(spec)
    import Surface
    plist = Surface.selected_surface_pieces(sel)
    return plist

# -----------------------------------------------------------------------------
#
def single_volume(mlist):

    if mlist is None:
        return mlist
    vlist = filter_volumes(mlist)
    if len(vlist) != 1:
        raise CommandError, 'Must specify only one volume'
    return vlist[0]

# -----------------------------------------------------------------------------
#
def surface_center_axis(surf, center, axis, csys):

    if center is None:
        have_box, box = surf.bbox()
        if have_box:
            c = box.center()
        else:
            from chimera import Point
            c = Point(0,0,0)
    elif csys:
        sixf = surf.openState.xform.inverse()
        c = sixf.apply(csys.xform.apply(center))
    else:
        c = center

    if axis is None:
        from chimera import Vector
        a = Vector(0,0,1)
    elif csys:
        sixf = surf.openState.xform.inverse()
        a = sixf.apply(csys.xform.apply(axis))
    else:
        a = axis

    return c.data(), a.data()

# -----------------------------------------------------------------------------
#
def parse_center_axis(center, axis, csys, cmdname):

    from Commands import parseCenterArg, parse_axis

    if isinstance(center, (tuple, list)):
        from chimera import Point
        center = Point(*center)
        ccs = csys
    elif center:
        center, ccs = parseCenterArg(center, cmdname)
    else:
        ccs = None

    if isinstance(axis, (tuple, list)):
        from chimera import Vector
        axis = Vector(*axis)
        acs = csys
    elif axis:
        axis, axis_point, acs = parse_axis(axis, cmdname)
    else:
        axis_point = None
        acs = None

    if not center and axis_point:
        # Use axis point if no center specified.
        center = axis_point
        ccs = acs

    # If no coordinate system specified use axis or center coord system.
    cs = (ccs or acs)
    if csys is None and cs:
        csys = cs
        xf = cs.xform.inverse()
        if center and not ccs:
            center = xf.apply(center)
        if axis and not acs:
            axis = xf.apply(axis)

    # Convert axis and center to requested coordinate system.
    if csys:
        xf = csys.xform.inverse()
        if center and ccs:
            center = xf.apply(ccs.xform.apply(center))
        if axis and acs:
            axis = xf.apply(acs.xform.apply(axis))

    return center, axis, csys

# -----------------------------------------------------------------------------
#
def parse_colormap(cmap, cmapRange, reverseColors):

    if not isinstance(cmap, basestring):
        raise CommandError, 'Invalid colormap specification: "%s"' % repr(cmap)

    pname = {'redblue': 'red-white-blue',
             'rainbow': 'rainbow',
             'gray': 'grayscale',
             'cyanmaroon': 'cyan-white-maroon'}
    if cmap.lower() in pname:
        from SurfaceColor import standard_color_palettes as scp
        rgba = scp[pname[cmap.lower()]]
        n = len(rgba)
        cmap = [(c/float(n-1),rgba[c]) for c in range(n)]
        if not cmapRange:
            cmapRange = 'full'
    else:
        vclist = cmap.split(':')
        if len(vclist) < 2:
            raise CommandError, 'Invalid colormap specification: "%s"' % cmap
        cmap = [parse_value_color(vc) for vc in vclist]

    if cmapRange:
        cmrerr = 'cmapRange must be "full" or two numbers separated by a comma'
        if not isinstance(cmapRange, basestring):
            raise CommandError, cmrerr

        if cmapRange.lower() == 'full':
            cmapRange = cmapRange.lower()
        else:
            try:
                cmapRange = [float(x) for x in cmapRange.split(',')]
            except ValueError:
                raise CommandError, cmrerr
            if len(cmapRange) != 2:
                raise CommandError, cmrerr

    if reverseColors:
        n = len(cmap)
        cmap = [(cmap[c][0],cmap[n-1-c][1]) for c in range(n)]

    return cmap, cmapRange

# -----------------------------------------------------------------------------
#
def parse_value_color(vc):

    err = 'Colormap entry must be value,color: got "%s"' % vc
    svc = vc.split(',',1)
    if len(svc) != 2:
        raise CommandError, err
    try:
        v = float(svc[0])
    except ValueError:
        raise CommandError, err
    from Commands import convertColor
    try:
        c = convertColor(svc[1]).rgba()
    except:
        raise CommandError, err
    return v, c

# -----------------------------------------------------------------------------
#
def parse_color(color):

    if isinstance(color, (tuple, list)):
        if len(color) == 4:
            return tuple(color)
        elif len(color) == 3:
            return tuple(color) + (1,)
    from Commands import convertColor
    try:
        c = convertColor(color).rgba()
    except:
        raise CommandError, 'Unrecognized color: "%s"' % repr(color)
    return c
