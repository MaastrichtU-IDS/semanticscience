# -----------------------------------------------------------------------------
# Syntax: hkcage <h> <k> <radius> <orientation> <line-thickness> <sphere-factor>
#
def hkcage_command(cmdname, args):

    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(hkcage, args)

# -----------------------------------------------------------------------------
#
def hkcage(h, k, radius = 100.0, orientation = '222', color = (1,1,1,1),
           linewidth = 1.0, sphere = 0.0, replace = True):

    from Midas.midas_text import error
    if not type(h) is int or not type(k) is int:
        error('h and k must be integers, got %s %s' % (repr(h), repr(k)))
        return

    if h < 0 or k < 0 or (h == 0 and k == 0):
        error('h and k must be non-negative and one > 0, got %d %d' % (h,k))
        return

    from chimera import MaterialColor
    if isinstance(color, MaterialColor):
        color = color.rgba()

    from Icosahedron import coordinate_system_names
    if not orientation in coordinate_system_names:
        error('Invalid orientation %s, must be one of: %s' %
              (orientation, ', '.join(coordinate_system_names)))
        return

    from cages import show_hk_lattice
    show_hk_lattice(h, k, radius, orientation, color, linewidth, sphere,
                    replace)
