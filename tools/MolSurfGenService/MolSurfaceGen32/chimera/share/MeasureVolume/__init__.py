# -----------------------------------------------------------------------------
# Calculate volume enclosed by a surface and surface area.
#
# Volume and area calculations ignore clipping and capping.
#
# TODO: Exclude hidden geometry from calculation.  Exclude undisplayed
#       surface components.
#
def surface_volume_and_area(model):

    volume, area, hole_count = surface_model_volume_and_area(model)
    return volume, area, hole_count

# -----------------------------------------------------------------------------
#
def surface_model_volume_and_area(model):

    volume = 0
    hole_count = 0
    area = 0
    plist = model.surfacePieces
    plist = [p for p in plist if not hasattr(p, 'outline_box')]
    import SurfaceCap
    plist = [p for p in plist if not SurfaceCap.is_surface_cap(p)]
    for p in plist:
        v, a, hc = surface_piece_volume_and_area(p)
        if volume != None:
            if v == None:
                volume = None
            else:
                volume += v
            hole_count += hc
        area += a
    return volume, area, hole_count

# -----------------------------------------------------------------------------
#
def surface_piece_volume_and_area(p):

    varray, tarray = p.geometry
    v, hc = enclosed_volume(varray, tarray)
    a = surface_area(varray, tarray)
    return v, a, hc

# -----------------------------------------------------------------------------
#
def enclosed_volume(varray, tarray):

    from _surface import enclosed_volume
    vol, hole_count = enclosed_volume(varray, tarray)
    if vol < 0:
        return None, hole_count
    return vol, hole_count

# -----------------------------------------------------------------------------
#
def surface_area(varray, tarray):

    from _surface import surface_area
    area = surface_area(varray, tarray)
    return area
    
# -----------------------------------------------------------------------------
#
def report_selected_areas():

    report_selected_volume_and_area(report_area = True)
    
# -----------------------------------------------------------------------------
#
def report_selected_volumes():

    report_selected_volume_and_area(report_volume = True)
    
# -----------------------------------------------------------------------------
#
def report_selected_volume_and_area(report_volume = False, report_area = False):

    slist = selected_surfaces()
    report_volume_and_area(slist, report_volume, report_area)
    if len(slist) > 1:
        show_reply_log()

# -----------------------------------------------------------------------------
#
def report_volume_and_area(slist, report_volume = False, report_area = False):

    from chimera.replyobj import info, status
    for s in slist:
        vstring = ''
        if report_volume:
            v, hc = volume(s)
            if v == None:
                vstring += ' volume = N/A (non-oriented surface)'
            else:
                vstring += ' volume = %.5g' % v
                if hc > 0:
                    vstring += ' (%d holes)' % hc
        if report_area:
            a = area(s)
            vstring += ' area = %.5g' % a
        msg = '%s: %s' % (surface_name(s), vstring)
        info(msg + '\n')

    if len(slist) == 1:
        status(msg)

# -----------------------------------------------------------------------------
#
def show_reply_log():

    from chimera import dialogs
    from chimera import tkgui
    dialogs.display(tkgui._ReplyDialog.name)

# -----------------------------------------------------------------------------
#
def area(s):

    varray, tarray = surface_geometry(s)
    area = surface_area(varray, tarray)
    return area

# -----------------------------------------------------------------------------
#
def volume(s):

    varray, tarray = surface_geometry(s)
    volume, hc = enclosed_volume(varray, tarray)
    return volume, hc

# -----------------------------------------------------------------------------
#
def surface_geometry(s):

    return s.geometry

# -----------------------------------------------------------------------------
#
def surface_name(s):

    pname = s.oslName
    if pname and pname != '?':
        name = s.model.name + ' ' + s.oslName
    else:
        name = s.model.name
    return name

# -----------------------------------------------------------------------------
#
def selected_surfaces():

    from Surface import selected_surface_pieces
    splist = selected_surface_pieces()
    splist.sort(lambda a,b: cmp(surface_name(a), surface_name(b)))
    return splist
    
# -----------------------------------------------------------------------------
#
def surface_models():

    from chimera import openModels
    from _surface import SurfaceModel
    mlist = openModels.list(modelTypes = [SurfaceModel])
    from SurfaceCap import is_surface_cap
    mlist = filter(lambda m: not is_surface_cap(m), mlist)

    return mlist
