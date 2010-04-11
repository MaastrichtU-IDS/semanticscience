# -----------------------------------------------------------------------------
# Added entry to Chimera fetch by id dialog to fetch biological unit PDB
# models from the Probable Quaternary Structure server.
#
import FetchPQS
FetchPQS.register_pqs_id_file_prefix()
FetchPQS.register_fetch_gui()
