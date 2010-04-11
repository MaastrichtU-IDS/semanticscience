# -----------------------------------------------------------------------------
# Command to calculate and display various measurements.
#
#   Syntax: measure <operation> <params>
#
# where operation and parameters are one of
#
#       rotation <mspec1> <mspec2> [showAxis True] [color blue]
#
#       volume <sspec>
#
#       area <sspec>
#
#       correlation <vspec1> <vspec2> [aboveThreshold True|False]
#                       [rotationAxis <spec>] [angleRange 0,360,2] [plot True]
#
#       buriedarea <aspec1> <aspec2> [probeRadius 1.4] [vertexDensity 2.0]
#
from Commands import CommandError
def measure_command(cmdname, args):

    operations = {'rotation': (rotation_axis, [('model1Spec','model1','models'),
                                             ('model2Spec','model2','models')]),
                  'volume': (volume_area, [('surfaceSpec','surface','models')]),
                  'area': (volume_area, [('surfaceSpec','surface','models')]),
                  'correlation': (correlation, [('map1Spec','map1','models'),
                                                ('map2Spec','map2','models')]),
                  'buriedArea': (buried_area, [('a1Spec','atoms1','atoms'),
                                                ('a2Spec','atoms2','atoms')]),
                  'inertia': (inertia, []),
                  }
    from Commands import abbreviation_table
    aop = abbreviation_table(operations.keys())

    fields = args.split(' ', 1)
    if len(fields) == 0:
        ops = ', '.join(operations.keys())
        raise CommandError, 'Missing required argument: "operation" (%s)' % ops
    op = aop.get(fields[0].lower())
    if op is None:
        ops = ', '.join(operations)
        raise CommandError, 'Unknown operation "%s" (use %s)' % (fields[0], ops)
        
    from Commands import doExtensionFunc
    f, specInfo = operations[op]
    doExtensionFunc(f, args, specInfo = specInfo)

# -----------------------------------------------------------------------------
#
def rotation_axis(operation, model1, model2,
                  showAxis = True, showSlabs = False, color = None):

    os1 = set([m.openState for m in model1])
    os2 = set([m.openState for m in model2])
    if len(os1) != 1:
        raise CommandError, 'First model spec names %d models, require 1' % len(os1)
    if len(os2) != 1:
        raise CommandError, 'Second model spec names %d models, require 1' % len(os2)
    os1 = os1.pop()
    os2 = os2.pop()

    xf = os1.xform.inverse()
    xf.multiply(os2.xform)
    import Matrix
    tf = Matrix.xform_matrix(xf)
    message = ('Position of %s (%s) relative to %s (%s) coordinates:\n'
               % (model2[0].name, model2[0].oslIdent(),
                  model1[0].name, model1[0].oslIdent()))
    message += Matrix.transformation_description(tf)
    from chimera import replyobj
    replyobj.info(message)

    from chimera import MaterialColor
    if isinstance(color, MaterialColor):
        color = color.rgba()
    elif not color is None:
        raise CommandError, 'Unknown color "%s"' % str(color)

    if showAxis:
        show_axis(tf, color, os1)

    if showSlabs:
        show_slabs(xf, color, os1)

# -----------------------------------------------------------------------------
#
def show_axis(tf, color, os):

    import Matrix
    axis, axis_point, angle, axis_shift = Matrix.axis_center_angle_shift(tf)
    if angle < 0.1:
        raise CommandError, 'Rotation angle is near zero (%g degrees)' % angle

    have_box, box = os.bbox()
    if not have_box:
        # TODO: Chimera does not provide bounding box of full model.
        raise CommandError, 'First model must be visible to show axis'

    axis_center = Matrix.project_to_axis(box.center().data(), axis, axis_point)
    axis_length = max((box.urb - box.llf).data())
    hl = 0.5*axis_length
    ap1 = map(lambda a,b: a-hl*b, axis_center, axis)
    ap2 = map(lambda a,b: a+hl*b, axis_center, axis)
    from VolumePath import Marker_Set, Link
    from VolumePath.markerset import chimera_color
    m = Marker_Set('rotation axis')
    mm = m.marker_model()
    mm.openState.xform = os.xform
    if color:
        mm.color = chimera_color(color)
    radius = 0.025 * axis_length
    m1 = m.place_marker(ap1, None, radius)
    m2 = m.place_marker(ap2, None, radius)
    Link(m1, m2, None, radius)

# -----------------------------------------------------------------------------
# xf is xform in os coordinates.
#
def show_slabs(xf, color, os):

    # Make schematic illustrating rotation
    if color is None:
        color = (.7,.7,.7,1)
    have_box, box = os.bbox()
    if not have_box:
        return
    center = box.center().data()
    import MatchDomains
    sm = MatchDomains.transform_schematic(xf, center, color, color)
    if sm:
        sm.name = 'slabs'
        from chimera import openModels as om
        om.add([sm])
        sm.openState.xform = os.xform
    return sm

# -----------------------------------------------------------------------------
#
def volume_area(operation, surface):

    from _surface import SurfaceModel
    slist = [s for s in surface if isinstance(s, SurfaceModel)]
    if len(slist) == 0:
        raise CommandError, 'No surfaces specified'

    import Surface
    plist = Surface.surface_pieces(slist)

    import MeasureVolume as m
    op = operation[0]
    m.report_volume_and_area(plist,
                             report_volume = (op == 'v'),
                             report_area = (op == 'a'))

# -----------------------------------------------------------------------------
#
def correlation(operation, map1, map2, aboveThreshold = True,
                rotationAxis = None, angleRange = (0,360,2),
                plot = True):

    from VolumeViewer import Volume
    map1 = [m for m in map1 if isinstance(m, Volume)]
    map2 = [m for m in map2 if isinstance(m, Volume)]
    if len(map1) == 0 or len(map2) == 0:
        raise CommandError, 'Must specify 2 maps'

    if rotationAxis:
        # Rotate map1 in steps and report correlations.
        from Commands import parse_axis
        axis, center, csys = parse_axis(rotationAxis, 'measure')
        if center is None:
            raise CommandError, 'Rotation axis must be atom/bond spec'
        axis = csys.xform.apply(axis).data()
        center = csys.xform.apply(center).data()
        if isinstance(angleRange, str):
            try:
                angleRange = [float(x) for x in angleRange.split(',')]
            except:
                angleRange = []
            if len(angleRange) != 3:
                raise CommandError, 'Angle range must be 3 comma-separated values, got "%s"' % angleRange

        for v1 in map1:
            for v2 in map2:
                report_correlations_with_rotation(v1, v2, aboveThreshold,
                                                  axis, center, angleRange,
                                                  plot)
    else:
        for v1 in map1:
            for v2 in map2:
                report_correlation(v1, v2, aboveThreshold)

# -----------------------------------------------------------------------------
#
def report_correlation(v1, v2, aboveThreshold):
            
    from chimera import replyobj
    import FitMap
    olap, cor = FitMap.map_overlap_and_correlation(v1, v2, aboveThreshold)
    replyobj.status('correlation = %.4g\n' % cor)
    replyobj.info('Correlation between %s and %s = %.4g\n'
                  % (v1.name, v2.name, cor))

# -----------------------------------------------------------------------------
#
def report_correlations_with_rotation(v1, v2, aboveThreshold,
                                      axis, center, angleRange, plot):

    from chimera import Vector, Point, replyobj

    # Convert axis and center to v1 local coordinates so transformation
    # is still valid if user rotates entire scene.
    xf = v1.openState.xform.inverse()
    axis = xf.apply(Vector(*axis)).data()
    center = xf.apply(Point(*center)).data()

    import FitMap, Matrix
    replyobj.info('Correlation between %s and %s\n' % (v1.name, v2.name) +
                  'Rotation\tCorrelation\n')
    a0, a1, astep = angleRange
    angle = a0
    clist = []
    from Matrix import multiply_matrices, xform_matrix, rotation_transform, chimera_xform
    while angle < a1:
        tf = multiply_matrices(xform_matrix(v1.openState.xform),
                               rotation_transform(axis, angle, center),
                               xform_matrix(v1.openState.xform.inverse()))
        xf = chimera_xform(tf)
        olap, cor = FitMap.map_overlap_and_correlation(v1, v2,
                                                       aboveThreshold, xf)
        replyobj.status('angle = %.4g, correlation = %.4g\n' % (angle, cor))
        replyobj.info('%.4g\t%.4g\n' % (angle, cor))
        clist.append((angle,cor))
        angle += astep

    if plot:
        angles = [a for a,c in clist]
        corr = [c for a,c in clist]
        plot_correlation(angles, corr, v1, v2, axis, center)

# -----------------------------------------------------------------------------
#
def plot_correlation(angles, corr, v1, v2, axis, center):

    # TODO: Make Tk plot window to use Chimera root window as master so it
    #       gets iconified when Chimera iconified.  Unfortunately matplotlib
    #       doesn't provide for setting Tk master.  Need to create our own
    #       Toplevel and embed the canvas as in embedding_in_tk.py example.
    #       Also see matplotlib.backends.backend_tkagg.new_figure_manager().
    import matplotlib.pyplot as plt
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    ax.plot(angles, corr, linewidth=1.0)
    ax.set_xlim(xmax = 360.0)
    ax.set_xticks(range(0,361,30))
    ax.set_ylim(ymax = 1.0)
    ax.set_xlabel('rotation angle (degrees)')
    ax.set_ylabel('correlation')
    ax.set_title('Correlation of rotated %s vs %s' % (v1.name, v2.name))
    ax.grid(True)
    ax.cur_position = plt.Line2D((0,0), ax.get_ylim(), linewidth = 1.0, color = 'orange')
    ax.add_line(ax.cur_position)
    def graph_event_cb(event, v1=v1, axis=axis, center=center, cur_angle = [0]):
        if not event.button is None:
            angle = event.xdata
            if angle is None:
                angle = 0       # Click outside graph bounds
            import Matrix
            tf = Matrix.rotation_transform(axis, angle-cur_angle[0], center)
            xf = Matrix.chimera_xform(tf)
            v1.openState.localXform(xf)
            cur_angle[0] = angle
            ax.cur_position.set_xdata((angle,angle))
            ax.figure.canvas.draw()

    fig.canvas.mpl_connect('button_press_event', graph_event_cb)
    fig.canvas.mpl_connect('motion_notify_event', graph_event_cb)
    fig.canvas.manager.show()

# -----------------------------------------------------------------------------
#
def buried_area(operation, atoms1, atoms2,
                probeRadius = 1.4, vertexDensity = 2.0):

    xyzr = atom_xyzr(atoms1 + atoms2)
    n1 = len(atoms1)
    xyzr1 = xyzr[:n1]
    xyzr2 = xyzr[n1:]
    xyzr12 = xyzr

    failed = False
    import MoleculeSurface as ms
    try:
        s1 = ms.xyzr_surface_geometry(xyzr1, probeRadius, vertexDensity)
        s2 = ms.xyzr_surface_geometry(xyzr2, probeRadius, vertexDensity)
        s12 = ms.xyzr_surface_geometry(xyzr12, probeRadius, vertexDensity)
    except ms.Surface_Calculation_Error:
        failed = True

    if failed or not s1[6] or not s2[6] or not s12[6]:
        # All component calculation failed.
        try:
            s1 = ms.xyzr_surface_geometry(xyzr1, probeRadius, vertexDensity,
                                          all_components = False)
            s2 = ms.xyzr_surface_geometry(xyzr2, probeRadius, vertexDensity,
                                          all_components = False)
            s12 = ms.xyzr_surface_geometry(xyzr12, probeRadius, vertexDensity,
                                           all_components = False)
        except ms.Surface_Calculation_Error:
            raise CommandError, 'Surface calculation failed.'
        from chimera import replyobj
        replyobj.warning('Calculation of some surface components failed.  Using only single surface component.  This may give inaccurate areas if surfaces of either set of atoms or the combined set are disconnected.\n')

    # Assign per-atom buried areas.
    aareas1, aareas2, aareas12 = s1[3], s2[3], s12[3]
    ases121 = asas121 = ases122 = asas122 = 0
    for ai,a in enumerate(atoms1):
        a.buriedSESArea = aareas1[ai,0] - aareas12[ai,0]
        a.buriedSASArea = aareas1[ai,1] - aareas12[ai,1]
        ases121 += aareas12[ai,0]
        asas121 += aareas12[ai,1]
    for ai,a in enumerate(atoms2):
        a.buriedSESArea = aareas2[ai,0] - aareas12[n1+ai,0]
        a.buriedSASArea = aareas2[ai,1] - aareas12[n1+ai,1]
        ases122 += aareas12[n1+ai,0]
        asas122 += aareas12[n1+ai,1]
    careas1, careas2, careas12 = s1[4], s2[4], s12[4]
    ases1, asas1 = area_sums(careas1)
    ases2, asas2 = area_sums(careas2)
    ases12, asas12 = area_sums(careas12)
    bsas1 = asas1 - asas121
    bsas2 = asas2 - asas122
    bsas = 0.5 * (bsas1 + bsas2)
    bses1 = ases1 - ases121
    bses2 = ases2 - ases122
    bses = 0.5 * (bses1 + bses2)

    # TODO: include atomspec's in output message.
    msg = ('Buried solvent accessible surface area\n'
           '  B1SAS = %.6g, B2SAS = %.6g, BaveSAS = %.6g\n'
           '  (A1 = %.6g, A2 = %.6g, A12 = %.6g = %.6g + %.6g)\n' %
           (bsas1, bsas2, bsas,asas1, asas2, asas12, asas121, asas122) + 
           'Buried solvent excluded surface area\n ' +
           '  B1SES = %.6g, B2SES = %.6g, BaveSES = %.6g\n'
           '  (A1 = %.6g, A2 = %.6g, A12 = %.6g = %.6g + %.6g)\n' %
           (bses1, bses2, bses,ases1, ases2, ases12, ases121, ases122))
    from chimera import replyobj
    replyobj.info(msg)

    smsg = 'Buried areas: SAS = %.6g, SES = %.6g\n' % (bsas, bses)
    replyobj.status(smsg)

# -----------------------------------------------------------------------------
#
def atom_xyzr(atoms):

    n = len(atoms)
    from numpy import zeros, float32
    xyzr = zeros((n,4), float32)
    for a in range(n):
        atom = atoms[a]
        xyz = atom.xformCoord().data()
        r = atom.radius
        xyzr[a,:] = xyz + (r,)
    return xyzr

# -----------------------------------------------------------------------------
#
def area_sums(careas):

    if len(careas) == 0:
        return 0,0
    import numpy
    return numpy.sum(careas, axis = 0)

# -----------------------------------------------------------------------------
#
def inertia(operation, objects, showEllipsoid = True, color = None,
            perChain = False):

    from chimera import specifier
    try:
        sel = specifier.evalSpec(objects)
    except:
        raise CommandError, 'Bad object specifier "%s"' % objects

    if not color is None:
        from Commands import parse_color
        color = parse_color(color)

    atoms = sel.atoms()
    if atoms:
        import inertia
        if perChain:
            xf = atoms[0].molecule.openState.xform
            mname = molecules_name(list(set([a.molecule for a in atoms])))
            s = inertia.surface_model(None, xf, 'ellipsoids ' + mname)
            for achain in atoms_by_chain(atoms):
                p = inertia.atoms_inertia_ellipsoid(achain, showEllipsoid,
                                                    color, s)
                if p:
                    p.oslName = achain[0].residue.id.chainId
        else:
            inertia.atoms_inertia_ellipsoid(atoms, showEllipsoid, color)

    import Surface
    plist = Surface.selected_surface_pieces(sel, include_outline_boxes = False)
    if plist:
        import inertia
        inertia.surface_inertia_ellipsoid(plist, showEllipsoid, color)

# ----------------------------------------------------------------------------
#        
def atoms_by_chain(atoms):

    chains = {}
    for a in atoms:
        k = (a.molecule, a.residue.id.chainId)
        if k in chains:
            chains[k].append(a)
        else:
            chains[k] = [a]
    return chains.values()

# ----------------------------------------------------------------------------
#        
def molecules_name(mlist):

    if len(mlist) == 1:
        return mlist[0].name
    return '%d molecules' % len(mlist)
