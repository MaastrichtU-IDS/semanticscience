# -----------------------------------------------------------------------------
#
class Surface_Calculation_Error(Exception):
    pass

# -----------------------------------------------------------------------------
#
def msms_geometry(atoms, probe_radius = 1.4, vertex_density = 2.0,
                  all_components = True, separate_process = True):

    n = len(atoms)
    
    from numpy import zeros, float32, subtract
    xyzr = zeros((n,4), float32)
    for a in range(n):
        atom = atoms[a]
        xyz = atom.coord().data()
        r = atom.radius
        xyzr[a,:] = xyz + (r,)

    vfloat, vint, tri, atomareas, compareas, srf, allcomp = \
      xyzr_surface_geometry(xyzr, probe_radius, vertex_density,
                            all_components, separate_process)
    return vfloat, vint, tri, atomareas, compareas, srf, allcomp

# -----------------------------------------------------------------------------
#
def xyzr_surface_geometry(xyzr, probe_radius = 1.4, vertex_density = 2.0,
                          all_components = True, separate_process = True):

    if len(xyzr) == 0:
        return empty_surface() + (None, all_components)

    if separate_process:
        vfloat, vint, tri, atomareas, compareas, allcomp = \
            run_mscalc(xyzr, probe_radius, vertex_density, all_components)
#        vfloat, vint, tri, atomareas = run_msms(xyzr, probe_radius,
#                                                vertex_density,
#                                                all_components)
        srf = None
    else:
        import mslib
        srf = mslib.MSMS(coords = xyzr, maxnat = len(xyzr))
        if all_components:
            srf.compute_rs(probe_radius, allComponents = 1)
            srf.compute_ses()
            srf.triangulate(vertex_density)
        else:
            srf.compute(probe_radius, vertex_density)
        srf.compute_ses_area()              # Analytic per-atom areas.
        srf.compute_numeric_area_vol()      # Triangulation per-atom areas
        vfloat, vint, tri = triangle_data(srf)
        atomareas, compareas = atom_areas(srf)
        allcomp = all_components

    return vfloat, vint, tri, atomareas, compareas, srf, allcomp

# -----------------------------------------------------------------------------
#
def triangle_data(srf):

    tdata = []
    while True:
        try:
            tdata.append(srf.getTriangles(component=len(tdata)))
        except:
            break   # No more components

    return combine_triangle_data(tdata)

# -----------------------------------------------------------------------------
# Combine triangulation data from all surface components.
#
# vfloat elements (x,y,z,nx,ny,nz,sesA,sasA)
# vint elements (type, closestAtomindex, buried)
# tri elements (i, j, k, type, SESF_num)
#
def combine_triangle_data(tdata):

    # Make atom indices start at 0.
    atom_base_index = 1
    for vf, vi, tr in tdata:
        vi[:,1] -= atom_base_index

    if len(tdata) == 0:
        return empty_surface()[:3]
    
    if len(tdata) == 1:
        return tdata[0]

    from numpy import concatenate
    vfloat = concatenate([vf for vf, vi, tr in tdata])
    vint = concatenate([vi for vf, vi, tr in tdata])
    tri = concatenate([tr for vf, vi, tr in tdata])

    # Adjust triangle indices.
    t = v = 0
    for vf, vi, tr in tdata:
        tri[t:t+len(tr),:3] += v
        t += len(tr)
        v += len(vf)

    return vfloat, vint, tri

# -----------------------------------------------------------------------------
# Get analytic per atom areas summed over all surface components and also
# total areas for each surface component.
# MSMS library doesn't wrap array of per-atom SES/SAS areas, just gives
# C pointer so there is some ugly use of ctypes.
#
def atom_areas(srf):

    from numpy import zeros, single as floatc, dtype, fromstring, double
    aareas = zeros((srf.nbat,2), floatc)
    nb = srf.rsr.nb
    careas = zeros((nb,2), floatc)
    for a in range(srf.nbat):
        atm = srf.get_atm(a)
        ses_comp_areas = doubles_from_pointer(atm.ses_area, nb)
        sas_comp_areas = doubles_from_pointer(atm.sas_area, nb)
        careas[:,0] += ses_comp_areas
        careas[:,1] += sas_comp_areas
        aareas[a] = (sum(ses_comp_areas), sum(sas_comp_areas))
    return aareas, careas

# -----------------------------------------------------------------------------
#
def doubles_from_pointer(swig_double_p, n):

    addr = swig_double_p
    if addr.startswith('_') and addr.endswith('_double_p'):
        addr = addr[1:-len('_double_p')]
    iaddr = int(addr, 16)
    from ctypes import string_at
    from numpy import double, dtype, fromstring
    s = string_at(iaddr, n*dtype(double).itemsize)
    a = fromstring(s, double)
    return a

# -----------------------------------------------------------------------------
#
def run_msms(xyzr, probe_radius = 1.4, vertex_density = 2.0,
             all_components = True):

    from CGLutil.findExecutable import findExecutable
    msms_path = findExecutable('msms')
    if msms_path is None:
        raise Surface_Calculation_Error, 'No msms executable found'

    # Write input file
    from tempfile import mkstemp
    fd, xyzr_path = mkstemp('.xyzr', 'surf')
    from os import write, close
    for x,y,z,r in xyzr:
        write(fd, '%12.5g %12.5g %12.5g %12.5g\n' % (x,y,z,r))
    close(fd)

    out_prefix = xyzr_path[:-5]
    area_path = out_prefix + '.area'

    if all_components:
        all = '-all_components'
    else:
        all = ''

    command = ('"%s" -if "%s" -of "%s" -af "%s" -probe_radius %.6g -density %.6g -no_header %s'
               % (msms_path, xyzr_path, out_prefix, area_path,
                  probe_radius, vertex_density, all))
    from chimera.replyobj import info
    info('Running command\n%s\n' % command)
    from os import system
    status = system(command)

    if status != 0:
        raise Surface_Calculation_Error, 'MSMS surface calculation failed, code %d' % status

    from os import remove
    remove(xyzr_path)

    vfloat, vint, tri, atomareas = read_msms_output(out_prefix, area_path)

    remove_msms_output(out_prefix, area_path)

    return vfloat, vint, tri, atomareas

# -----------------------------------------------------------------------------
#
def read_msms_output(prefix, area_path):

    tdata = []
    while True:
        td = read_msms_component_output(prefix, len(tdata))
        if td is None:
            break
        tdata.append(td)

    vfloat, vint, tri = combine_triangle_data(tdata)

    atomareas = read_atom_areas(area_path)

    return vfloat, vint, tri, atomareas

# -----------------------------------------------------------------------------
#
def read_msms_component_output(prefix, component):
    
    if component > 0:
        prefix += '_%d' % component

    # Read vertices
    try:
        vf = open(prefix + '.vert')
    except:
        return None
    vlines = vf.readlines()
    vf.close()

    nv = len(vlines)
    from numpy import zeros, single as floatc, intc
    vfloat = zeros((nv,8), floatc)
    vint = zeros((nv,3), intc)
    for v, line in enumerate(vlines):
        fields = line.split()
        vfloat[v,:6] = [float(x) for x in fields[0:6]]
        vint[v,:] = [int(x) for x in fields[6:9]]

    # Read triangles.
    try:
        tf = open(prefix + '.face')
    except:
        return None
    tlines = tf.readlines()
    tf.close()

    nt = len(tlines)
    tri = zeros((nt,5), intc)
    for t, line in enumerate(tlines):
        fields = line.split()
        tri[t,:] = [int(x)-1 for x in fields]
    
    return vfloat, vint, tri

# -----------------------------------------------------------------------------
#
def remove_msms_output(prefix, area_path):

    from os.path import exists
    from os import remove
    component = 0
    while True:
        if component > 0: p = prefix + ('_%d' % component)
        else: p = prefix
        vpath = p  + '.vert'
        if exists(vpath): remove(vpath)
        else: break
        tpath = p + '.face'
        if exists(tpath): remove(tpath)
        else: break
        component += 1

    if exists(area_path):
        remove(area_path)

# -----------------------------------------------------------------------------
#
def read_atom_areas(area_path):

    f = open(area_path)
    lines = f.readlines()
    f.close()

    from numpy import zeros, single as floatc
    atomareas = zeros((len(lines)-1,2), floatc)
    for a,line in enumerate(lines[1:]):
        areas = [float(area) for area in line.split()[1:]]
        atomareas[a,:] = (sum(areas[::2]), sum(areas[1::2]))

    return atomareas

# -----------------------------------------------------------------------------
#
def run_mscalc(xyzr, probe_radius = 1.4, vertex_density = 2.0,
               all_components = True, fallback_to_single_component = True):

    from CGLutil.findExecutable import findExecutable
    mscalc_path = findExecutable('mscalc')
    if mscalc_path is None:
        raise Surface_Calculation_Error, 'No mscalc executable found'

    if all_components: allc = '1'
    else: allc = '0'

    args = (mscalc_path, '%f' % probe_radius, '%f' % vertex_density, allc)

    from numpy import array, intc
    xyzrs = array(len(xyzr),intc).tostring() + xyzr.tostring()

    cmd = ' '.join(args)
    from chimera.replyobj import info
    info(cmd + '\n')

    msout, mserr, status = run_shell_command(args, xyzrs)
    if status is None:
        raise Surface_Calculation_Error, 'Starting mscalc failed.'

    if mserr:
        info(mserr)

    try:
        if status != 0:
            raise Surface_Calculation_Error, 'Surface calculation failed, mscalc returned code %d' % status

        vfloat, vint, tri, atomareas, compareas = parse_mscalc_output(msout)

        if atomareas is None and len(xyzr) > 0:
            raise Surface_Calculation_Error, 'Surface calculation failed, produced empty surface.\n'
    except Surface_Calculation_Error:
        if fallback_to_single_component and all_components:
            from chimera.replyobj import warning
            warning('Calculation of some surface components failed.\nFalling back to single-component calculation.\n')
            return run_mscalc(xyzr, probe_radius, vertex_density,
                              all_components = False)
        raise

    return vfloat, vint, tri, atomareas, compareas, all_components

# -----------------------------------------------------------------------------
#
def run_shell_command(args, input):

    # Hide console window on Windows.
    import sys
    if sys.platform == 'win32':
        from subprocess import STARTUPINFO, STARTF_USESHOWWINDOW
        spinfo = STARTUPINFO()
        spinfo.dwFlags |= STARTF_USESHOWWINDOW
    else:
        spinfo = None

    from subprocess import Popen, PIPE
    try:
        p = Popen(args, stdin = PIPE, stdout = PIPE,  stderr = PIPE,
                  startupinfo = spinfo)
    except:
        return None, None, None

    # Use communicate() to read stdout and stderr without blocking.
    msout, mserr = p.communicate(input = input) # returns strings
    status = p.wait()
    return msout, mserr, status

# -----------------------------------------------------------------------------
#
def parse_mscalc_output(msouts):

    from cStringIO import StringIO
    msout = StringIO(msouts)

    from numpy import fromstring, intc, single as floatc
    ncomps = msout.read(4)
    if len(ncomps) == 4:
        ncomp = fromstring(ncomps, intc)[0]
    else:
        ncomp = 0
    tdata = []
    atomareas = None
    compareas = []
    for n in range(ncomp):
        vfloat = read_binary_array(msout, 8, floatc)
        vint = read_binary_array(msout, 3, intc)
        tri = read_binary_array(msout, 5, intc)
        tdata.append((vfloat, vint, tri))
        areas = read_binary_array(msout, 2, floatc)
        if atomareas is None:
            atomareas = areas
        else:
            atomareas += areas
        compareas.append(areas.sum(axis = 0))
    vfloat, vint, tri = combine_triangle_data(tdata)

    return vfloat, vint, tri, atomareas, compareas

# -----------------------------------------------------------------------------
#
def write_binary_array(a, f):

    from numpy import array, intc
    f.write(array(len(a),intc).tostring())
    f.write(a.tostring())

# -----------------------------------------------------------------------------
#
def read_binary_array(f, d2, type):

    from numpy import fromstring, intc, dtype
    n = fromstring(f.read(4), intc)
    if len(n) != 1:
        raise Surface_Calculation_Error, 'Surface calculation failed, truncated output.\n'
    n = n[0]

    t = dtype(type)
    a1d = fromstring(f.read(t.itemsize * n * d2), t)
    if len(a1d) != n*d2:
        raise Surface_Calculation_Error, 'Surface calculation failed, truncated output.\n'
    a = a1d.reshape((n,d2))
    return a

# -----------------------------------------------------------------------------
#
def empty_surface():

    from numpy import zeros, single as floatc, intc
    return (zeros((0,8), floatc),       # vfloat
            zeros((0,3), intc),         # vint
            zeros((0,5), intc),         # tri
            zeros((0,2), floatc),       # per-atom surface areas
            [],                         # component surface areas
            )
