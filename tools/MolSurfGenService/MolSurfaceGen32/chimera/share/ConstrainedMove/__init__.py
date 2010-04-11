# -----------------------------------------------------------------------------
# Provide mouse modes to allow rotation about a specified axis, and to confine
# translations to an axis, or a plane.
#
import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Constrained_Move_Dialog(ModelessDialog):

    title = 'Constrained Move'
    name = 'constrained move'
    buttons = ('Close',)
    help = 'ContributedSoftware/constrained/constrained.html'

    def fillInUI(self, parent):

        self.last_xy = None
        
        import Tkinter
        from CGLtk import Hybrid

        parent.columnconfigure(0, weight = 1)
        row = 0
        
        cr = Hybrid.Checkbutton(parent, 'Constrain mouse rotations', 0)
        cr.button.grid(row = row, column = 0, sticky = 'w')
        row = row + 1
        self.constrain_rotations = cr.variable
        cr.callback(self.constrain_rotation_cb)

        raf = Tkinter.Frame(parent)
        raf.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        ra = Hybrid.Entry(raf, 'Axis ', 8, '0 0 1')
        ra.frame.grid(row = 0, column = 0, sticky = 'w')
        self.rot_axis = ra.variable

        rotx_cb = lambda v=self.rot_axis: v.set('1 0 0')
        roty_cb = lambda v=self.rot_axis: v.set('0 1 0')
        rotz_cb = lambda v=self.rot_axis: v.set('0 0 1')
        rab = Hybrid.Button_Row(raf, ' ',
                                (('x', rotx_cb),
                                 ('y', roty_cb),
                                 ('z', rotz_cb)))
        rab.frame.grid(row = 0, column = 1, sticky = 'w')

        rof = Tkinter.Frame(parent)
        rof.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        ro = Hybrid.Entry(rof, 'Origin ', 8, '0 0 0')
        ro.frame.grid(row = 0, column = 0, sticky = 'w')
        self.rot_origin = ro.variable

        zorigin_cb = lambda v=self.rot_origin: v.set('0 0 0')
        rob = Hybrid.Button_Row(rof, ' ',
                                (('zero', zorigin_cb),
                                 ('center', self.set_rotation_origin_at_center),))
        rob.frame.grid(row = 0, column = 1, sticky = 'w')

        sep = Tkinter.Frame(parent,  relief = Tkinter.GROOVE,
                            borderwidth=1, height=2)
        sep.grid(row = row, column = 0, sticky = 'ew', pady = 10)
        row = row + 1
        
        tr = Hybrid.Checkbutton(parent, 'Constrain mouse translations', 0)
        tr.button.grid(row = row, column = 0, sticky = 'w')
        row = row + 1
        self.constrain_translations = tr.variable
        tr.callback(self.constrain_translation_cb)

        taf = Tkinter.Frame(parent)
        taf.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        ta = Hybrid.Entry(taf, 'Axis ', 8, '0 0 1')
        ta.frame.grid(row = 0, column = 0, sticky = 'w')
        self.trans_axis = ta.variable

        tx_cb = lambda v=self.trans_axis: v.set('1 0 0')
        ty_cb = lambda v=self.trans_axis: v.set('0 1 0')
        tz_cb = lambda v=self.trans_axis: v.set('0 0 1')
        tab = Hybrid.Button_Row(taf, ' ',
                                (('x', tx_cb),
                                 ('y', ty_cb),
                                 ('z', tz_cb)))
        tab.frame.grid(row = 0, column = 1, sticky = 'w')

        ttf = Tkinter.Frame(parent)
        ttf.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        tt = Hybrid.Option_Menu(ttf, 'Allow only ',
                                'parallel', 'perpendicular')
        tt.variable.set('parallel')
        tt.frame.grid(row = 0, column = 0, sticky = 'w')
        self.translation_type = tt.variable
        
        tl = Tkinter.Label(ttf, text = ' motion')
        tl.grid(row = 0, column = 1, sticky = 'w')

        sep = Tkinter.Frame(parent,  relief = Tkinter.GROOVE,
                            borderwidth=1, height=2)
        sep.grid(row = row, column = 0, sticky = 'ew', pady = 10)
        row = row + 1

        rl = Tkinter.Label(parent, text = 'Axis and origin relative to')
        rl.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        mmf = Tkinter.Frame(parent)
        mmf.grid(row = row, column = 0, sticky = 'w')
        row = row + 1

        mm = Hybrid.Option_Menu(mmf, 'model ')
        mm.frame.grid(row = 0, column = 0, sticky = 'w')
        self.model_menu = mm
        self.model_name = mm.variable
        from chimera import openModels
        openModels.addAddHandler(self.model_list_changed_cb, None)
        openModels.addRemoveHandler(self.model_list_changed_cb, None)
                
        ml = Tkinter.Label(mmf, text = ' coordinates.')
        ml.grid(row = 0, column = 1, sticky = 'w')

        self.update_model_menu()
        self.register_mouse_modes()
        
    # -------------------------------------------------------------------------
    #
    def update_model_menu(self):

        menu = self.model_menu
        menu.remove_all_entries()
        mnames = self.model_table().keys()
        for name in mnames:
            menu.add_entry(name)

        if len(mnames) > 0 and self.model_name.get() == '':
            self.model_name.set(mnames[0])
        
    # -------------------------------------------------------------------------
    #
    def model_table(self):

        mtable = {}
        from chimera import openModels
        for m in openModels.list():
            if hasattr(m, 'name') and m.name:
                name = m.name
            else:
                name = 'id #%d' % m.id
            if mtable.has_key(name):
                suffix_num = 1
                while mtable.has_key(name + '<%d>' % suffix_num):
                    suffix_num += 1
                name = name + '<%d>' % suffix_num
            mtable[name] = m
        return mtable

    # -------------------------------------------------------------------------
    #
    def model_list_changed_cb(self, *unused):

        self.update_model_menu()
        
    # -------------------------------------------------------------------------
    #
    def constrain_rotation_cb(self):

        self.set_mouse_mode(self.constrain_rotations.get(),
                            'rotate', 'constrained rotation')

    # -------------------------------------------------------------------------
    #
    def constrain_translation_cb(self):

        self.set_mouse_mode(self.constrain_translations.get(),
                            'translate x,y', 'constrained translation')

    # -------------------------------------------------------------------------
    #
    def set_mouse_mode(self, constrain, unconstrained_mode_name,
                       constrained_mode_name):

        find_binding = self.find_mouse_binding
        uc_button, uc_modifiers = find_binding(unconstrained_mode_name)
        c_button, c_modifiers = find_binding(constrained_mode_name)
        if constrain:
            if c_button == None and uc_button:
                from chimera import mousemodes
                mousemodes.setButtonFunction(uc_button, uc_modifiers,
                                             constrained_mode_name)
            # TODO: should warn if no button is assigned
        else:
            if c_button and uc_button == None:
                from chimera import mousemodes
                mousemodes.setButtonFunction(c_button, c_modifiers,
                                             unconstrained_mode_name)
        
    # -------------------------------------------------------------------------
    #
    def find_mouse_binding(self, mode_name):

        from chimera import mousemodes
        modifier_combinations = all_subsets(mousemodes.usedMods)
        for button in mousemodes.usedButtons:
            for modifiers in modifier_combinations:
                name = mousemodes.getFuncName(button, modifiers)
                if name == mode_name:
                    return (button, modifiers)

        return (None, None)

    # -------------------------------------------------------------------------
    #
    def register_mouse_modes(self):

        # mode: (press, motion, release [, double press, double release])
        rotate_funcs = (
            self.start_rotation_cb,
            self.rotation_cb,
            self.stop_rotation_cb
            )
        rotate_icon = mouse_mode_icon('roticon.png')
        from chimera import mousemodes
        mousemodes.addFunction('constrained rotation', rotate_funcs,
                               rotate_icon)

        translate_funcs = (
            self.start_translation_cb,
            self.translation_cb,
            self.stop_translation_cb
            )
        translate_icon = mouse_mode_icon('transicon.png')
        mousemodes.addFunction('constrained translation', translate_funcs,
                               translate_icon)

    # -------------------------------------------------------------------------
    #
    def start_rotation_cb(self, v, e):
        v.recordPosition(e.time, e.x, e.y, "rotate")
        self.last_xy = (e.x, e.y)
    def rotation_cb(self, v, e):
        axis = self.rotation_axis()
        origin = self.rotation_origin()
        xy = (e.x, e.y)
        if self.last_xy == None:
            self.last_xy = xy
        if axis and not is_zero_vector(axis) and origin:
            rotate_around_axis(axis, origin, xy, self.last_xy)
        else:
            from chimera import replyobj
            replyobj.status('Constrained move: Invalid rotation axis or origin.',
                            blankAfter = 3, color = 'red')
        self.last_xy = xy
    def stop_rotation_cb(self, v, e):
        v.setCursor(None)
        self.last_xy = None

    # -------------------------------------------------------------------------
    #
    def start_translation_cb(self, v, e):
        v.recordPosition(e.time, e.x, e.y, "translate x/y")
        self.last_xy = (e.x, e.y)
    def translation_cb(self, v, e):
        axis = self.translation_axis()
        xy = (e.x, e.y)
        if self.last_xy == None:
            self.last_xy = xy
        if axis and not is_zero_vector(axis):
            parallel = (self.translation_type.get() == 'parallel')
            if parallel:
                translate_parallel_to_axis(axis, xy, self.last_xy)
            else:
                translate_perpendicular_to_axis(axis, xy, self.last_xy)
        else:
            from chimera import replyobj
            replyobj.status('Constrained move: Invalid translation axis.',
                            blankAfter = 3, color = 'red')
        self.last_xy = xy
    def stop_translation_cb(self, v, e):
        v.setCursor(None)
        self.last_xy = None

    # -------------------------------------------------------------------------
    #
    def rotation_axis(self):
        return self.model_vector(self.rot_axis.get())
    def rotation_origin(self):
        return self.model_point(self.rot_origin.get())
    def translation_axis(self):
        return self.model_vector(self.trans_axis.get())

    # -------------------------------------------------------------------------
    # Convert string vector from model coordinates to Chimera coordinates.
    #
    def model_vector(self, model_vector_string):
    
        try:
            data_axis = map(float, model_vector_string.split())
        except ValueError:
            data_axis = None

        if data_axis == None or len(data_axis) != 3:
            return None

        m = self.model()
        if m == None:
            return None

        dav = apply(chimera.Vector, data_axis)
        av = m.openState.xform.apply(dav)

        return (av.x, av.y, av.z)

    # -------------------------------------------------------------------------
    # Convert string point from model coordinates to Chimera coordinates.
    #
    def model_point(self, model_point_string):
    
        try:
            model_point = map(float, model_point_string.split())
        except ValueError:
            model_point = None

        if model_point == None or len(model_point) != 3:
            return None

        m = self.model()
        if m == None:
            return None

        mp = apply(chimera.Point, model_point)
        p = m.openState.xform.apply(mp)

        return (p.x, p.y, p.z)
        
    # -------------------------------------------------------------------------
    #
    def set_rotation_origin_at_center(self):

        m = self.model()
        if m == None:
            return

        have_box, box = m.bbox()
        if not have_box:
            return
        
        center = box.llf + (box.urb - box.llf) * .5
        cstring = '%.5g %.5g %.5g' % (center.x, center.y, center.z)
        self.rot_origin.set(cstring)
        
    # -------------------------------------------------------------------------
    #
    def model(self):

        mtable = self.model_table()
        name = self.model_name.get()
        if mtable.has_key(name):
            return mtable[name]
        return None

# -----------------------------------------------------------------------------
#
def rotate_around_axis(axis, origin, screen_xy, last_screen_xy):

    # Measure drag around axis with mouse on front clip plane.
    sx, sy = screen_xy
    from VolumeViewer import slice
    xyz, back_xyz = slice.clip_plane_points(sx, sy)
    lsx, lsy = last_screen_xy
    last_xyz, back_last_xyz = slice.clip_plane_points(lsx, lsy)

    a = apply(chimera.Vector, axis)
    a.normalize()
    o = apply(chimera.Vector, origin)
    v = apply(chimera.Vector, xyz)
    lv = apply(chimera.Vector, last_xyz)
    t = chimera.cross(a, v - o)
    t2 = t.sqlength()
    if t2 > 0:
        angle = (t * (v - lv)) / t2
    else:
        angle = 0

    import math
    angle_deg = 180 * angle / math.pi
    
    vo = apply(chimera.Vector, origin)
    va = apply(chimera.Vector, axis)

    xf = chimera.Xform()
    xf.translate(vo)
    xf.rotate(va, angle_deg)
    xf.translate(-vo)
    # Applying xf performs the two translations and rotations in the
    # opposite order of the function calls.  First it translates by -vo,
    # then rotates, then translates by +vo.
    
    move_active_models(xf)

# -----------------------------------------------------------------------------
#
def translate_parallel_to_axis(axis, screen_xy, last_screen_xy):

    psize = pixel_size()
    d = chimera.Vector((screen_xy[0] - last_screen_xy[0]) * psize,
                       -(screen_xy[1] - last_screen_xy[1]) * psize,
                       0)
    a = apply(chimera.Vector, axis)
    a.normalize()
    t = a * (a*d)

    xf = chimera.Xform.translation(t)
    move_active_models(xf)

# -----------------------------------------------------------------------------
#
def translate_perpendicular_to_axis(axis, screen_xy, last_screen_xy):

    psize = pixel_size()
    d = chimera.Vector((screen_xy[0] - last_screen_xy[0]) * psize,
                       -(screen_xy[1] - last_screen_xy[1]) * psize,
                       0)
    a = apply(chimera.Vector, axis)
    a.normalize()
    t = d - a * (a*d)

    xf = chimera.Xform.translation(t)
    move_active_models(xf)
    
# -----------------------------------------------------------------------------
#
def move_active_models(xf):
    
    for os in open_state_objects():
        if os.active:
            os.globalXform(xf)
    
# -----------------------------------------------------------------------------
# Pixel size at front clip plane.
#
def pixel_size():
    
    c = chimera.viewer.camera
    view = 0
    llx, lly, width, height = c.viewport(view)
    left, right, bottom, top, znear, zfar, f = c.window(view)
    psize = (right - left) / width
    return psize
    
# -----------------------------------------------------------------------------
#
def open_state_objects():

    models = chimera.openModels.list(all = True)
    ostable = {}
    for m in models:
        os = m.openState
        ostable[os] = 1
    oslist = ostable.keys()
    return oslist
            
# -----------------------------------------------------------------------------
#
def all_subsets(seq):

    if len(seq) == 0:
        return ((),)
    s0 = seq[0]
    subsets = []
    for subset in all_subsets(seq[1:]):
        subsets.append(subset)
        subsets.append((s0,) + subset)
    return tuple(subsets)

# -----------------------------------------------------------------------------
#
def is_zero_vector(v):

    return v[0] == 0 and v[1] == 0 and v[2] == 0

# -----------------------------------------------------------------------------
#
def mouse_mode_icon(file_name):

    import os.path
    icon_path = os.path.join(os.path.dirname(__file__), file_name)
    from PIL import Image
    image = Image.open(icon_path)
    from chimera import chimage
    from chimera import tkgui
    icon = chimage.get(image, tkgui.app)
    return icon

# -----------------------------------------------------------------------------
#
def constrained_move_dialog(create=0):

  from chimera import dialogs
  return dialogs.find(Constrained_Move_Dialog.name, create=create)

# -----------------------------------------------------------------------------
#
def show_constrained_move_dialog():

  from chimera import dialogs
  return dialogs.display(Constrained_Move_Dialog.name)
    
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Constrained_Move_Dialog.name, Constrained_Move_Dialog,
                 replace = 1)
