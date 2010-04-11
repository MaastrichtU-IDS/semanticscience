# -----------------------------------------------------------------------------
# Multi-key accelerators.
#
      
# -----------------------------------------------------------------------------
#
class Accelerator:

  def __init__(self, key_sequence, short_description, function):

    self.key_sequence = key_sequence
    self.short_descrip = short_description
    self.function = function
    
  # ---------------------------------------------------------------------------
  #
  def invoke(self):

    self.function()
    
  # ---------------------------------------------------------------------------
  #
  def short_description(self):

    return self.short_descrip
  
  # ---------------------------------------------------------------------------
  #
  def long_description(self):

    if hasattr(self.function, 'func_doc'):
      doc = self.function.func_doc
      if doc:
        return doc
    return 'No documentation'

# -----------------------------------------------------------------------------
#
class Accelerator_Table:
  
  def __init__(self):

    self.accel_table = {}       # Maps key sequence to Accelerator object
    self.prefix_table = {}
    
  # ---------------------------------------------------------------------------
  #
  def add_accelerator(self, key_sequence, short_description, function):

    a = Accelerator(key_sequence, short_description, function)
    self.accel_table[key_sequence] = a
    for k in range(1, len(key_sequence)):
      prefix = key_sequence[:k]
      self.prefix_table[prefix] = 1
    
  # ---------------------------------------------------------------------------
  #
  def accelerators(self):

    return self.accel_table.values()

  # ---------------------------------------------------------------------------
  #
  def find_accelerator(self, key_seq):
    
    if key_seq in self.accel_table:
      return self.accel_table[key_seq]
    return None
  
  # ---------------------------------------------------------------------------
  #
  def is_accelerator_prefix(self, key_seq):

    return key_seq in self.prefix_table
  
  # ---------------------------------------------------------------------------
  #
  def remove_all_accelerators(self):

    self.accel_table = {}
    self.prefix_table = {}

# -----------------------------------------------------------------------------
#
def default_accelerator_file():

  import os.path
  dir = os.path.dirname(__file__)
  default_path = os.path.join(dir, 'standard_accelerators.py')
  return default_path

# -----------------------------------------------------------------------------
#
prefcat = None
def accelerator_preferences_category():

  global prefcat
  if prefcat is None:
    options = {
      'path': default_accelerator_file(),
      'time out': '2',
      'enable at startup': None,
      }
    from chimera import preferences as preferences
    prefcat = preferences.addCategory('Accelerators',
                                      preferences.HiddenCategory,
                                      optDict=options)
  return prefcat

  
# -----------------------------------------------------------------------------
# Autostart accelerators if preferences file requests it.
#
def autostart_accelerators():

  import chimera
  if chimera.nogui:
    return
  cat = accelerator_preferences_category()
  enable = cat['enable at startup']
  if enable is None:
    # Check auto-start preference from old Chimera versions (< 1.2509)
    from chimera.extension import manager, makeExtensionKey
    enable = manager.autoStart.get(makeExtensionKey('Accelerators On'), False)
  if enable:
    activate_accelerators(True)
  
# -----------------------------------------------------------------------------
#
def add_accelerator(key_sequence, short_description, function):

  t = accelerator_table()
  t.add_accelerator(key_sequence, short_description, function)
  
# -----------------------------------------------------------------------------
#
def run_accelerator(key_sequence):

  t = accelerator_table()
  a = t.find_accelerator(key_sequence)
  if a:
    a.invoke()
  
# -----------------------------------------------------------------------------
#
def remove_all_accelerators():

  t = accelerator_table()
  t.remove_all_accelerators()
    
# -----------------------------------------------------------------------------
#
def activate_accelerators(active):

  d = accelerator_dialog(create = 1)
  d.activate(active)
  
# -----------------------------------------------------------------------------
#
def accelerator_command(cmdname, args):
  
  d = accelerator_dialog(create = True)
  d.accelerator_command(cmdname, args)

# -----------------------------------------------------------------------------
#
accel_table = None
def accelerator_table():

  global accel_table
  if accel_table == None:
    accel_table = Accelerator_Table()
  return accel_table
  
# -----------------------------------------------------------------------------
#
def accelerator_dialog(create = False):

  from gui import Accelerator_Browser
  from chimera import dialogs
  return dialogs.find(Accelerator_Browser.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_accelerator_dialog():

  from gui import Accelerator_Browser
  from chimera import dialogs
  return dialogs.display(Accelerator_Browser.name)
