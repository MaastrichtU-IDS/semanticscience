# -----------------------------------------------------------------------------
# Added entry to Chimera fetch by id dialog to fetch crystallographic density
# maps from the Upsalla Electron Density Server (EDS).
#
import FetchEDS
FetchEDS.register_eds_id_file_prefix()
FetchEDS.register_fetch_gui()
