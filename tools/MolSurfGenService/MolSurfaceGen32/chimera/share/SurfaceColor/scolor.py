# -----------------------------------------------------------------------------
# Code for scolor (spatial coloring) command, providing the campabilities of
# the Surface Color dialog.
#
#   Syntax: scolor <surfaceSpec>
#               [volume <vspec>]
#               [gradient <vspec>]
#               [geometry radial|cylindrical|height]
#               [color <color>]
#               [center <x,y,z>|<atomspec>]
#               [axis x|y|z|<x,y,z>|<atomspec,atomspec>]
#               [coordinateSystem <modelid>]
#               [cmap <v,color>:<v,color>:...|rainbow|gray|redblue|cyanmaroon]
#               [cmapRange <min,max>|full]
#		[reverseColors true|false]
#		[colorOutsideVolume <color>]
#               [offset <d>|<d1,d2,n>]
#               [autoUpdate true|false]
#               [capOnly true|false]
#               [perPixel true|false]
#
from Commands import CommandError
def scolor_command(cmdname, args):
    
    from Commands import doExtensionFunc, parse_enumeration
    if cmdname.startswith('un'):
        if len(args) == 0:
            args = '#'
        doExtensionFunc(unscolor, args,
                        specInfo = [('surfaceSpec','surfaces','models'),])
    else:
        sa = args.split(None, 2)
        if len(sa) < 2:
            raise CommandError, 'scolor requires at least 2 arguments: scolor <surf> <method>'
        sspec = ('surfaceSpec','surfaces','models')
        vspec = ('volumeSpec','volume','models')
        gspec = ('gradientSpec', 'gradient', 'models')
        cspec = ('coordinateSystemSpec','coordinateSystem','models')
        methods = {
        'color': (color_op, [sspec]),
        'geometry': (geometry_op, [sspec, cspec]),
        'gradient': (gradient_op, [sspec, gspec]),
        'volume': (volume_op, [sspec, vspec]),
        }
        method = parse_enumeration(sa[1], methods.keys())
        if method is None:
            raise CommandError, 'Unknown scolor method: %s' % sa[1]
        func, spec = methods[method]
        doExtensionFunc(func, args, specInfo = spec)

# -----------------------------------------------------------------------------
#
def color_op(surfaces, color = None):

    from Commands import parse_surfaces, parse_color
    surfs = parse_surfaces(surfaces)

    if color == 'byatom':
        from chimera import MSMSModel
        if [s for s in surfs if not isinstance(s, MSMSModel)]:
            raise CommandError, 'Cannot color byatom non-molecular surfaces'
    elif not color is None:
        color = parse_color(color)

    for surf in surfs:
        import SurfaceColor as sc
        sc.stop_coloring_surface(surf)
        if color == 'byatom':
            surf.colorMode = surf.ByAtom
        elif not color is None:
            import Surface
            Surface.set_coloring_method('static', surf)
            from chimera import MSMSModel
            if isinstance(surf, MSMSModel):
                surf.customRGBA = [color] * surf.vertexCount
            else:
                for p in surf.surfacePieces:
                    p.color = color

# -----------------------------------------------------------------------------
#
def geometry_op(surfaces, geometry = None,
                center = None, axis = None, coordinateSystem = None,
                cmap = 'redblue', cmapRange = None, reverseColors = False,
                autoUpdate = True, capOnly = False):

    from Commands import parse_surfaces, parse_colormap
    from Commands import parse_center_axis, surface_center_axis
    surfs = parse_surfaces(surfaces)

    geom = ('radial', 'cylindrical', 'height')
    from Commands import abbreviation_table
    gat = abbreviation_table(geom)
    g = gat.get(geometry.lower())
    if g is None:
        raise CommandError, ('Unknown geometry "%s", use %s'
                             % (geometry, ', '.join(geom)))
    geometry = g

    if not coordinateSystem is None:
        csys = set([cs.openState for cs in coordinateSystem])
        if len(csys) != 1:
            raise CommandError, 'Coordinate system must specify exactly one model'
        coordinateSystem = csys.pop()
    center, axis, coordinateSystem = parse_center_axis(center, axis,
                                                       coordinateSystem,
                                                       'scolor')

    cmap, cmapRange = parse_colormap(cmap, cmapRange, reverseColors)

    import SurfaceColor as sc
    for surf in surfs:
        cs = {'radial': sc.Radial_Color,
              'cylindrical': sc.Cylinder_Color,
              'height': sc.Height_Color}[geometry]()
        # Convert axis, center to coordinate system
        c,a = surface_center_axis(surf, center, axis, coordinateSystem)
        if cs.uses_origin:
            cs.set_origin(c)
        if cs.uses_axis:
            cs.set_axis(a)
        cm = colormap(cs, cmap, cmapRange, capOnly, surf)
        cs.set_colormap(cm)
        sc.color_surface(surf, cs, capOnly, autoUpdate)

# -----------------------------------------------------------------------------
#
def gradient_op(surfaces, gradient = None, cmap = 'redblue', cmapRange = None,
                reverseColors = False, colorOutsideVolume = 'gray', offset = 0,
                autoUpdate = True, capOnly = False):

    from Commands import parse_surfaces, single_volume
    from Commands import parse_color, parse_colormap
    surfs = parse_surfaces(surfaces)
    gradient = single_volume(gradient)
    if colorOutsideVolume:
        colorOutsideVolume = parse_color(colorOutsideVolume)
    cmap, cmapRange = parse_colormap(cmap, cmapRange, reverseColors)
    offset = parse_offset(offset)
    
    import SurfaceColor as sc
    for surf in surfs:
        cs = sc.Gradient_Color()
        cs.set_volume(gradient)
        cs.offset = offset
        cm = colormap(cs, cmap, cmapRange, capOnly, surf, colorOutsideVolume)
        cs.set_colormap(cm)
        sc.color_surface(surf, cs, capOnly, autoUpdate)

# -----------------------------------------------------------------------------
#
def volume_op(surfaces, volume = None, cmap = 'redblue', cmapRange = None,
              reverseColors = False, colorOutsideVolume = 'gray', offset = 0,
              autoUpdate = True, capOnly = False, perPixel = False):

    from Commands import parse_surfaces, single_volume
    from Commands import parse_color, parse_colormap
    surfs = parse_surfaces(surfaces)
    volume = single_volume(volume)
    if colorOutsideVolume:
        colorOutsideVolume = parse_color(colorOutsideVolume)
    cmap, cmapRange = parse_colormap(cmap, cmapRange, reverseColors)
    offset = parse_offset(offset)

    import SurfaceColor as sc
    for surf in surfs:
        cs = sc.Volume_Color()
        cs.set_volume(volume)
        cs.offset = offset
        cm = colormap(cs, cmap, cmapRange, capOnly, surf, colorOutsideVolume)
        cs.set_colormap(cm)
        cs.per_pixel_coloring = perPixel
        sc.color_surface(surf, cs, capOnly, autoUpdate)

# -----------------------------------------------------------------------------
#
def parse_offset(offset):

    from Commands import check_number, parse_floats
    if isinstance(offset, (basestring,tuple,list)):
        o1, o2, n = parse_floats(offset, 'offset', 3)
        if n <= 1:
            raise CommandError, 'Offset count must be greater than 1'
        offset = [o1 + (o2-o1)*float(i)/(n-1) for i in range(n)]
    else:
        check_number(offset, 'offset')
    return offset

# -----------------------------------------------------------------------------
#
def unscolor(surfaces):

    from _surface import SurfaceModel
    surfs = set([s for s in surfaces if isinstance(s, SurfaceModel)])
    if len(surfs) == 0:
        raise CommandError, 'No surfaces specified'
    import SurfaceColor as sc
    for s in surfs:
        sc.stop_coloring_surface(s)

# -----------------------------------------------------------------------------
#
def colormap(cs, cmap, cmap_range, cap_only, surf, color_no_value = None):

    import SurfaceColor as sc
    if cmap_range:
        if cmap_range == 'full':
            v0,v1 = sc.surface_value_range(surf, cs.value_range, cap_only)
            if v0 == None:
                v0,v1 = (0,1)
        else:
            v0,v1 = cmap_range
        vc = [(v0+v*(v1-v0), c) for v,c in cmap]
    else:
        vc = cmap
    cm = sc.Color_Map([v for v,c in vc], [c for v,c in vc],
                      color_no_value = color_no_value)
    return cm
