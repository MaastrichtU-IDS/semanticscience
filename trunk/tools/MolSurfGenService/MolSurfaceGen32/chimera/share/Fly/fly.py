# -----------------------------------------------------------------------------
# Command to smoothly interpolate between saved model positions and
# orientations and camera settings.
#
#  Syntax: fly [frames] <posname1> [frames1] <posname2> [frames2] ... <posnameN>
#
# This is similar to the reset command but performs cubic
# interpolation instead of piecewise linear interpolation and provides
# a more convenient syntax for motion through several positions.
#
from Midas import MidasError
def fly_command(cmdname, args):

    fields = args.split()
    if len(fields) < 1:
        raise MidasError, 'Syntax: fly [frames] <posname1> [frames1] <posname2> [frames2] ... <posnameN>'

    framestep = 1
    pnames = []
    frames = []
    for f, arg in enumerate(fields):
        try:
            c = int(arg)
        except ValueError:
            pnames.append(arg)
            frames.append(framestep)
        else:
            if f == 0:
                framestep = c
            elif frames:
                frames[-1] = c
    frames = frames[:-1]

    from Midas import positions
    for pname in pnames:
        if not pname in positions:
            raise MidasError, 'fly: Unknown position name "%s"' % pname

    params, open_states = view_parameters(pnames)
    from VolumePath import spline
    fparams = spline.overhauser_spline_points(params, frames,
                                              limit_tangent = 1.0)

    Fly_Playback(fparams, open_states)

# -----------------------------------------------------------------------------
#
def view_parameters(pnames):

    from Midas import positions, MidasError
    from chimera import openModels as om

    # Get sequence of all open states.
    osxf = {}
    closed = set()
    for pname in pnames:
        for mid in positions[pname][5].keys():
            try:
                osxf[om.openState(*mid)] = None
            except ValueError:
                closed.add(mid)        # model closed
    open_states = osxf.keys()

    # Set initial position.
    for mid,xf in positions[pnames[0]][5].items():
        if not mid in closed:
            om.openState(*mid).xform = xf

    # Find center of rotation.  Same center used for all models.
    from chimera import openModels as om
    have_sphere, s = om.bsphere()
    if not have_sphere:
        raise MidasError, 'fly: Nothing displayed to calculate center of rotation'
    center = s.center

    # Create camera/position/orientation parameter array for interpolation
    from numpy import empty, float32
    from math import log
    params = empty((len(pnames),8+10*len(open_states)), float32)
    for i,pname in enumerate(pnames):
        vscale, vsize, ccenter, cnearfar, cfocal, xforms = positions[pname][:6]
        p = params[i,:]
        p[0] = log(vscale)
        p[1] = vsize
        p[2:5] = ccenter
        p[5:7] = cnearfar
        p[7] = cfocal
        for mid, xf in xforms.items():
            if not mid in closed:
                osxf[om.openState(*mid)] = xf
        for oi, o in enumerate(open_states):
            pxf = p[8 + oi*10:]
            c = o.xform.inverse().apply(center)
            rotq, trans = xform_parameters(osxf[o], c)
            pxf[0:4] = rotq
            pxf[4:7] = c
            pxf[7:10] = trans

    return params, open_states

# -----------------------------------------------------------------------------
#
class Fly_Playback:

    def __init__(self, frame_params, open_states):

        self.frame_count = 0
        self.frame_params = frame_params
        self.open_states = open_states
        from chimera import triggers as t
        self.handler = t.addHandler('new frame', self.new_frame_cb, None)

    def new_frame_cb(self, tname, cdata, tdata):

        fc = self.frame_count
        self.frame_count += 1
        fp = self.frame_params
        if fc >= len(fp):
            from chimera import triggers as t
            self.handler = t.deleteHandler('new frame', self.handler)
            return

        # Camera parameters
        from chimera import Point, viewer as v
        from math import exp
        c = v.camera
        cp = fp[fc][:8]
        v.scaleFactor = exp(cp[0])
        v.viewSize = cp[1]
        c.center = tuple(cp[2:5])
        c.nearFar = tuple(cp[5:7])
        c.focal = cp[7]
                    
        # Model positions
        for i,os in enumerate(self.open_states):
            op = fp[fc][10*i+8:10*i+18]
            rotq = op[0:4]
            rotc = op[4:7]
            trans = op[7:10]
            os.xform = parameter_xform(rotq, rotc, trans)

# -----------------------------------------------------------------------------
# Convert Xform to quaternion and translation.
#
def xform_parameters(xf, rotc):

    t = xf.getTranslation()
    from chimera import Vector
    c = Vector(*rotc)
    trans = t - c + xf.apply(c)
    axis, angle = xf.getRotation()
    from math import pi, sin, cos
    a = angle * pi/180
    sa2 = sin(a/2)
    ca2 = cos(a/2)
    rotq = (sa2*axis[0], sa2*axis[1], sa2*axis[2], ca2)
    return rotq, trans.data()

# -----------------------------------------------------------------------------
# Convert quaternion, rotation center and translation to an Xform.
#
def parameter_xform(rotq, rotc, trans):

    import Matrix as m
    ttf = m.translation_matrix(trans)
    sa2 = m.norm(rotq[:3])
    ca2 = rotq[3]
    from math import atan2, pi
    angle = 2*atan2(sa2,ca2) * 180.0/pi
    axis = m.normalize_vector(rotq[:3])
    rtf = m.rotation_transform(axis, angle, rotc)
    tf = m.multiply_matrices(ttf, rtf)
    xf = m.chimera_xform(tf)
    return xf
