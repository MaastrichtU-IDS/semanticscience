import chimera.extension

# -----------------------------------------------------------------------------
#
class Shininess_EMO(chimera.extension.EMO):

  def name(self):
    return 'Shininess'
  def description(self):
    return 'Adjust specular highlights on models'
  def categories(self):
    return ['Viewing Controls']
  def icon(self):
    return self.path('h2o_icon.png')
  def activate(self):
    self.module().display()
    return None

# -----------------------------------------------------------------------------
#
emo = Shininess_EMO(__file__)
chimera.extension.manager.registerExtension(emo)
