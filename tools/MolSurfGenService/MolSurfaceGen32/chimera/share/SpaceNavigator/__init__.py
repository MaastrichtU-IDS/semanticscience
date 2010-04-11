# -----------------------------------------------------------------------------
#
class Space_Navigator:

    def __init__(self):

        self.speed = 1
        self.dominant = True    # Don't simultaneously rotate and translate
        self.zoom = True        # Z-motion zooms.
        self.all_models = False # Move inactive models.
        self.fly_mode = False   # Control camera instead of models.

        from chimera import nogui
        if nogui:
            return
        
        try:
            self.device = find_device()
        except:
            return      # Connection failed.  TODO: report failure.

        if self.device:
            from chimera import triggers as t
            t.addHandler('new frame', self.check_space_navigator, None)

    def check_space_navigator(self, trigger_name, d1, d2):

        e = self.device.last_event()
        if e is None:
            return
        rot, trans, buttons = e

        from math import sqrt, pow
        from chimera import Vector, Xform, viewer

        # Rotation
        rx, ry, rz = rot         # 10 bits, signed, +/-512
        rmag = sqrt(rx*rx + ry*ry + rz*rz)

        # Translation
        tx, ty, tz = trans       # 10 bits, signed, +/-512
        if self.zoom and not self.fly_mode:
            zm = tz
            tz = 0
        else:
            zm = 0
        tmag = sqrt(tx*tx + ty*ty + tz*tz)
        zmag = abs(zm)
        
        if self.dominant:
            if tmag < rmag or tmag < zmag:
                tmag = 0
            if rmag < tmag or rmag < zmag:
                rmag = 0
            if zmag < tmag or zmag < rmag:
                zmag = 0
            if self.fly_mode:
                rt = 50
                if abs(ry) > abs(rx)+rt and abs(ry) > abs(rz)+rt: rx = rz = 0
                else: ry = 0
                rmag = sqrt(rx*rx + ry*ry + rz*rz)

        if rmag > 0:
            axis = Vector(rx/rmag, ry/rmag, rz/rmag)
            if self.fly_mode: f = 3
            else: f = 30
            angle = self.speed*(f*rmag/512)
            xf = Xform.rotation(axis, angle)
            self.apply_transform(xf)

        if tmag > 0:
            axis = Vector(tx/tmag, ty/tmag, tz/tmag)
            shift = axis * 0.15 * self.speed * viewer.viewSize * tmag/512
            xf = Xform.translation(shift)
            self.apply_transform(xf)

        if zmag != 0:
            f = pow(1.1, self.speed*float(zm)/512)
            import Midas
            Midas.updateZoomDepth(viewer)
            try:
                viewer.scaleFactor *= f
            except ValueError:
                import chimera
		raise chimera.LimitationError("refocus to continue scaling")

        if 'N1' in buttons or 31 in buttons:
            self.view_all()

        if 'N2' in buttons:
            self.toggle_dominant_mode()

    def apply_transform(self, xf):

        # Apply transform to models.
        from chimera import viewer, openModels as om, Point
        oslist = list(set([m.openState for m in om.list()]))

        # Activate inactive models in fly mode or all models mode.
        ialist = []
        if self.fly_mode or self.all_models:
            ialist = [os for os in set([m.openState for m in om.list()])
                      if not os.active]
            for os in ialist:
                os.active = True

        if self.fly_mode:
            m, c = om.cofrMethod, om.cofr
            om.cofrMethod = om.Fixed
            view = 0            # TODO: use center between eyes for stereo
            e = Point(*viewer.camera.eyePos(view))
            om.cofr = e         # Rotate about eye position
            om.applyXform(xf.inverse())
            om.cofr = c         # Restore center of rotation
            om.cofrMethod = m
        else:
            om.applyXform(xf)

        for os in ialist:
            os.active = False

    def toggle_zoom_mode(self):

        self.zoom = not self.zoom
        from chimera.replyobj import status
        status('z motion zooms: %s' % self.zoom)

    def toggle_dominant_mode(self):

        self.dominant = not self.dominant
        from chimera.replyobj import status
        status('simultaneous rotation and translation: %s'
               % (not self.dominant))

    def toggle_all_models(self):

        self.all_models = not self.all_models
        from chimera.replyobj import status
        status('move inactive models: %s' % self.all_models)

    def toggle_fly_mode(self):

        self.fly_mode = not self.fly_mode
        from chimera import viewer
        viewer.clipping = False
        from chimera.replyobj import status
        status('fly through mode: %s' % self.fly_mode)

    def view_all(self):

        from chimera import viewer
        viewer.viewAll()

# -----------------------------------------------------------------------------
#
def find_device():

    from sys import platform
    if platform == 'darwin':
        from snavmac import Space_Device_Mac
        return Space_Device_Mac()
    elif platform == 'win32':
        from snavwin32 import Space_Device_Win32
        return Space_Device_Win32()
    elif platform[:5] == 'linux':
        from snavlinux import Space_Device_Linux
        return Space_Device_Linux()

    return None

# -----------------------------------------------------------------------------
#
sn = Space_Navigator()
