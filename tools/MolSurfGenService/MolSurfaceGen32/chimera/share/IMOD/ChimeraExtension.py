# -----------------------------------------------------------------------------
# Register IMOD file reader, for display segmentation mesh surfaces.
#
def open_cb(path):
    import IMOD
    mlist = IMOD.read_imod_segmentation(path, mesh = True, contours = False)
    return mlist

import chimera
fi = chimera.fileInfo
fi.register('IMOD segmentation', open_cb, ['.imod', '.mod'], ['imod'],
            canDecompress = False, category = fi.GENERIC3D)
