def surfdist():
  import SurfaceDistance
  SurfaceDistance.selection_surface_distance()

from Accelerators import add_accelerator
add_accelerator('sd', 'Report distance between selected atoms and displayed surfaces', surfdist)
