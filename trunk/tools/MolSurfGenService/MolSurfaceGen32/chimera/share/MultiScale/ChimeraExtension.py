import chimera.extension

class MultiScale_EMO(chimera.extension.EMO):
  def name(self):
    return 'Multiscale Models'
  def description(self):
    return 'Show multiscale model dialog'
  def categories(self):
    return ['Higher-Order Structure']
  def icon(self):
    return self.path('multiscale_icon.png')
  def activate(self):
    self.module().show_multiscale_model_dialog()
    return None

# -----------------------------------------------------------------------------
#
emo = MultiScale_EMO(__file__)
chimera.extension.manager.registerExtension(emo)

# -----------------------------------------------------------------------------
#
execfile(emo.path('accelerators.py'), {})     # Register keyboard shortcuts
execfile(emo.path('viper_file_reader.py'), {})      # Register file reader
