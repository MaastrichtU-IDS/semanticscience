# -----------------------------------------------------------------------------
# Command to perform surface operations.
#
#   Syntax: sop <operation> <surfaceSpec>
#               [spacing <d>]
#               [modelId <n>]
#               [inPlace true|false]
#
# where allowed operations are: finerMesh
#
from Commands import CommandError

def sop_command(cmdname, args):

    operations = {
        'finerMesh': (subdivide_op, []),
        }
    ops = operations.keys()

    sa = args.split(None, 2)
    if len(sa) < 2:
        raise CommandError, 'sop requires at least 2 arguments: sop <operation> <args...>'

    from Commands import parse_enumeration
    op = parse_enumeration(sa[0], ops)
    if op is None:
        raise CommandError, 'Unknown sop operation: %s' % sa[0]

    func, spec = operations[op]
    from Commands import doExtensionFunc
    fargs = ' '.join(sa[1:])
    doExtensionFunc(func, fargs, specInfo = spec)

# -----------------------------------------------------------------------------
#
def subdivide_op(surfaces, spacing = None, inPlace = False, modelId = None):

    from Commands import parse_surface_pieces, check_number, parse_model_id
    plist = parse_surface_pieces(surfaces)
    if len(plist) == 0:
        raise CommandError, 'No surfaces specified'
    if spacing is None:
        raise CommandError, 'Must specify mesh spacing'
    check_number(spacing, 'spacing', positive = True)
    model_id = parse_model_id(modelId)
    if inPlace:
        s = None
    else:
        from _surface import SurfaceModel
        s = SurfaceModel()
        s.name = 'finer mesh'
        from chimera import openModels as om
        if model_id:
            id, subid = model_id
        else:
            id, subid = om.Default, om.Default
        om.add([s], baseId = id, subid = subid)
        s.openState.xform = plist[0].model.openState.xform
    from subdivide import subdivide
    for p in plist:
        np = subdivide(p, spacing, s)
        if np != p:
            np.save_in_session = True
