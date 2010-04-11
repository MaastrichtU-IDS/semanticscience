from chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class Volume_Statistics_EMO(EMO):

  def name(self):
    return 'Volume Mean, SD, RMS'

  def description(self):
    return 'Calculates mean, standard deviation, and root mean square for volume data'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module().show_volume_statistics()
    return None

# -----------------------------------------------------------------------------
#
manager.registerExtension(Volume_Statistics_EMO(__file__))

# -----------------------------------------------------------------------------
#
def show_stats():
  from VolumeStatistics import show_volume_statistics
  show_volume_statistics(show_reply_log = False)

from Accelerators import add_accelerator
add_accelerator('md', 'Print mean and standard deviation of volume data',
		show_stats)
