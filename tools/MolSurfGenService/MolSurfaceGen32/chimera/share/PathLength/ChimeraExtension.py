# -----------------------------------------------------------------------------
#
def print_path_length():
    import PathLength
    PathLength.print_path_length()
def print_model_path_lengths():
    import PathLength
    PathLength.print_model_path_lengths()

# -----------------------------------------------------------------------------
#
from Accelerators import add_accelerator
add_accelerator('pl', 'Show total length of selected bonds', print_path_length)
add_accelerator('pL', 'Show total length of selected bonds for each model',
                print_model_path_lengths)
