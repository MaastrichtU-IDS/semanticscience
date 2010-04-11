# -----------------------------------------------------------------------------
#
def show_volume_statistics(show_reply_log = True):
    
    from VolumeViewer import active_volume
    dr = active_volume()
    if dr == None:
        message('No volume data opened', show_reply_log)
        return

    m = dr.matrix()
    mean, sd, rms = mean_sd_rms(m)
    descrip = subregion_description(dr)
    message('%s%s: mean = %.5g, SD = %.5g, RMS = %.5g'
            % (dr.name, descrip, mean, sd, rms),
            show_reply_log)

# -----------------------------------------------------------------------------
#
def mean_sd_rms(m):

    from numpy import float32
    mean = m.mean(dtype=float32)
    sd = m.std(dtype=float32)
    from math import sqrt
    rms = sqrt(sd*sd + mean*mean)
    return mean, sd, rms

# -----------------------------------------------------------------------------
#
def subregion_description(v):

    dlist = []
    ijk_min, ijk_max, ijk_step = [tuple(ijk) for ijk in v.region]
    if ijk_step != (1,1,1):
        if ijk_step[1] == ijk_step[0] and ijk_step[2] == ijk_step[0]:
            dlist.append('step %d' % ijk_step[0])
        else:
            dlist.append('step %d %d %d' % ijk_step)
    dmax = tuple([s-1 for s in v.data.size])
    if ijk_min != (0,0,0) or ijk_max != dmax:
        dlist.append('subregion')
    if dlist:
        return ' (' + ', '.join(dlist) + ')'
    return ''

# -----------------------------------------------------------------------------
#
def message(text, show_reply_log = False):

    from chimera.replyobj import message, status
    message(text + '\n')
    status(text, blankAfter = 0)

    if show_reply_log:
        from Accelerators.standard_accelerators import show_reply_log as srl
        srl()

# -----------------------------------------------------------------------------
#
def sphere_mean_rms_sd(m, ijk_to_xyz, center, radius):

    zsize, ysize, xsize = m.shape
    cx, cy, cz = center
    r2 = radius * radius
    s = s2 = n = 0
    for z in range(zsize):
        for y in range(ysize):
            for x in range(xsize):
                xyz = ijk_to_xyz((i,j,k))
                dx, dy, dz = map(lambda a,b: a - b, xyz, center)
                if dx*dx + dy*dy + dz*dz <= radius:
                    v = float(m[z,y,x])
                    s += v
                    s2 += v*v
                    n += 1
    a = s / n
    a2 = s2 / n
    import math
    rms = math.sqrt(a2)
    sd2 = a2 - a*a
    sd = math.sqrt(sd2)
    return a, rms, sd
    
