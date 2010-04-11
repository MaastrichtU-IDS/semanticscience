# -----------------------------------------------------------------------------
# Provide an Undo Move to undo model rotations and translations.
#

# -----------------------------------------------------------------------------
#
class Position_Recorder:

    def __init__(self):

        self.position_history = []
        self.redo_history = []
        self.history_size_limit = 100

        import chimera
        mh_id = chimera.triggers.addHandler(chimera.MOTION_STOP,
                                            self.record_model_positions, None)
        self.motion_stop_handler_id = mh_id
        ah_id = chimera.openModels.addAddHandler(self.record_model_positions,
                                                 None)
        self.add_model_handler_id = ah_id

        self.record_model_positions()
        
    # -------------------------------------------------------------------------
    #
    def undo_position_change(self):

        self.record_model_positions()
        h = self.position_history
        if len(h) < 2:
            return

        rh = self.redo_history
        rh.append(h.pop())

        limit = self.history_size_limit
        if len(rh) > limit:
            del rh[0:-limit]

        self.set_model_positions(h[-1])

    # -------------------------------------------------------------------------
    #
    def redo_position_change(self):

        self.record_model_positions()
        rh = self.redo_history
        if len(rh) == 0:
            return

        h = self.position_history
        h.append(rh.pop())
        self.set_model_positions(h[-1])

    # -------------------------------------------------------------------------
    #
    def record_model_positions(self, *unused):

        mp = self.model_positions()
        h = self.position_history
        if h:
            last_mp = h[-1]
            if self.same_positions(mp, last_mp):
                if self.extra_positions(mp, last_mp):
                    h.pop()
                else:
                    return

        h.append(mp)

        limit = self.history_size_limit
        if len(h) > limit:
            del h[0:-limit]

    # -------------------------------------------------------------------------
    #
    def model_positions(self):

        mp = {}
        for os in self.open_state_objects():
            mp[os] = os.xform
        return mp
            
    # -------------------------------------------------------------------------
    #
    def set_model_positions(self, mp):

        for os in self.open_state_objects():
            if mp.has_key(os):
                os.xform = mp[os]

    # -------------------------------------------------------------------------
    #
    def same_positions(self, mp1, mp2):

        import chimera
        angle_tolerance = 1e-5
        translation_tolerance = 1e-5
        for os, xf1 in mp1.items():
            if mp2.has_key(os):
                xf2 = mp2[os]
                xf = chimera.Xform()
                xf.multiply(xf1)
                xf.invert()
                xf.multiply(xf2)
                trans = xf.getTranslation()
                axis, angle = xf.getRotation()
                if (abs(angle) > angle_tolerance or
                    trans.length > translation_tolerance):
                    return False
        return True

    # -------------------------------------------------------------------------
    #
    def extra_positions(self, mp1, mp2):

        for os, xf1 in mp1.items():
            if not mp2.has_key(os):
                return True
        return False
    
    # -------------------------------------------------------------------------
    #
    def open_state_objects(self):

        import chimera
        models = chimera.openModels.list(all = True)
        ostable = {}
        for m in models:
            os = m.openState
            ostable[os] = 1
        oslist = ostable.keys()
        return oslist

# -----------------------------------------------------------------------------
#
precorder = None
def position_recorder():
    global precorder
    if precorder == None:
        precorder = Position_Recorder()
    return precorder

# -----------------------------------------------------------------------------
#
def start_recording():
    position_recorder()
def undo_move():
    position_recorder().undo_position_change()
def redo_move():
    position_recorder().redo_position_change()
