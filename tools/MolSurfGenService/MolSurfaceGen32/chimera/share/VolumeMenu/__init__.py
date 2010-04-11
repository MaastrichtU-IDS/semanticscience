# -----------------------------------------------------------------------------
#
def toplevel_volume_menu(action = 'toggle'):

    if action == 'show-delayed':
        from chimera import triggers
        arg = []
        h = triggers.addHandler('new frame', delayed_show, arg)
        arg.append(h)
        return

    if action == 'toggle':
        if volume_menu_shown_preference():
            action = 'hide'
        else:
            action = 'show'

    if action == 'show':
        create_toplevel_volume_menu()
        set_volume_menu_shown_preference(True)
    elif action == 'hide':
        remove_toplevel_volume_menu()
        set_volume_menu_shown_preference(False)

# -----------------------------------------------------------------------------
#
def delayed_show(trigger_name, h, fnum):

    from chimera import triggers
    triggers.deleteHandler('new frame', h[0])
    toplevel_volume_menu('show')

# -----------------------------------------------------------------------------
#
def volume_menu_shown_preference():

    return volume_menu_preferences().get('shown')

# -----------------------------------------------------------------------------
#
def set_volume_menu_shown_preference(shown):

    volume_menu_preferences().set('shown', shown)

# -----------------------------------------------------------------------------
#
vmpref = None
def volume_menu_preferences():

    global vmpref
    if vmpref is None:
        from chimera import preferences
        vmpref = preferences.addCategory('Volume Menu',
                                         preferences.HiddenCategory,
                                         optDict = {'shown': False})
    return vmpref

# -----------------------------------------------------------------------------
#
def create_toplevel_volume_menu():

    from chimera.tkgui import app, updateAquaMenuBar
    menubar = app.menubar
    if hasattr(menubar, 'volume_menu'):
        return
    import Tkinter
    vmenu = Tkinter.Menu(menubar, title='Volume', name='volume')
    menubar.volume_menu = vmenu
    from chimera.extension import manager
    cat = manager.findCategory('Volume Data')
    for e in cat.sortedEntries():
        vmenu.add_command(label = e.name(),
                          command = lambda e=e, cat=cat: e.menuActivate(cat))
    menubar.insert_cascade('Tools', label = 'Volume', underline = 0,
                           menu = vmenu)
    updateAquaMenuBar(menubar)

# -----------------------------------------------------------------------------
#
def remove_toplevel_volume_menu():

    from chimera.tkgui import app, updateAquaMenuBar
    menubar = app.menubar
    if not hasattr(menubar, 'volume_menu'):
        return
    menubar.delete('Volume')
    menubar.volume_menu.destroy()
    delattr(menubar, 'volume_menu')
    updateAquaMenuBar(menubar)
