# -----------------------------------------------------------------------------
#
from chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class SAXS_EMO(EMO):

    def name(self):
        return 'Small-Angle X-Ray Profile'
    def description(self):
        return 'Compute small angle x-ray scattering profile'
    def categories(self):
        return ['Higher-Order Structure']
    def icon(self):
        return None
    def activate(self):
        self.module('gui').show_saxs_dialog()
        return None

# -----------------------------------------------------------------------------
#
manager.registerExtension(SAXS_EMO(__file__))
