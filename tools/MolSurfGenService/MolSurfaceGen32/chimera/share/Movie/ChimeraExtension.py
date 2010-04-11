# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class MovieEMO(chimera.extension.EMO):
    def name(self):
        return 'MD Movie'
    def description(self):
        return 'Playback of MD Trajectories'
    def categories(self):
        return ['MD/Ensemble Analysis']
    def icon(self):
        return self.path('Icons/movie_title.png')
    def activate(self):
	# Call the 'Movie' function in the "__init__.py" module.
        self.module().Movie()
	return None

chimera.extension.manager.registerExtension(MovieEMO(__file__))

def openMovie(fileName):
	import Movie
	Movie.Movie(fileName)
	return []
chimera.fileInfo.register('movie', openMovie, None, ['md', 'movie'],
		category=chimera.FileInfo.DYNAMICS)

# Register coordset command.
def coordset(cmdname, args):
  from Movie.coordset import coordset
  coordset(cmdname, args)
from Midas.midas_text import addCommand
addCommand('coordset', coordset, help = True)
