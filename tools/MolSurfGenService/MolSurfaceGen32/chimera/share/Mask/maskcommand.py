# -----------------------------------------------------------------------------
# Command to extract a piece of a volume data set within a surface.
#
#   mask <volumes> <surfaces>
#        [axis <x,y,z>]
#        [fullMap true|false]
#        [pad <d>]
#        [slab <width>|<d1,d2>]
#        [sandwich true|false]
#
#   mask #0 #1 axis 0,0,1 fullmap true pad 10
#
# masks volume #0 using surface #1 via projection along the z axis, and
# makes a full copy of the map (rather than a minimal subregion) and expands
# the surface along its per-vertex normal vectors before masking.
#
def mask_command(cmdname, args):

    from Commands import doExtensionFunc
    doExtensionFunc(mask, args,
                    specInfo = [('volumeSpec','volumes','models'),
                                ('surfaceSpec','surfaces',None)])

# -----------------------------------------------------------------------------
#
def mask(volumes, surfaces, axis = None, fullMap = False,
         pad = 0., slab = None, sandwich = True, invertMask = False):

    from Commands import CommandError, filter_volumes, parse_floats
    vlist = filter_volumes(volumes)

    from Surface import selected_surface_pieces
    glist = selected_surface_pieces(surfaces, include_outline_boxes = False)
    if len(glist) == 0:
        raise CommandError, 'No surfaces specified'

    axis = parse_floats(axis, 'axis', 3, (0,1,0))

    if not isinstance(fullMap, (bool,int)):
        raise CommandError, 'fullMap option value must be true or false'

    if not isinstance(invertMask, (bool,int)):
        raise CommandError, 'invertMask option value must be true or false'

    if not isinstance(pad, (float,int)):
        raise CommandError, 'pad option value must be a number'

    if isinstance(slab, (float,int)):
        pad = (-0.5*slab, 0.5*slab)
    elif not slab is None:
        pad = parse_floats(slab, 'slab', 2)

    if not isinstance(sandwich, bool):
        raise CommandError, 'sandwich option value must be true or false'

    from depthmask import surface_geometry, masked_volume
    from Matrix import xform_matrix, invert_matrix
    for v in vlist:
        tf = invert_matrix(xform_matrix(v.model_transform()))
        surfs = surface_geometry(glist, tf, pad)
        masked_volume(v, surfs, axis, fullMap, sandwich, invertMask)
