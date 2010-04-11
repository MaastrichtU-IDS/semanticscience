// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---
//
// $Id: ChimeraPath.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef CHIMERA_CHIMERAPATHFINDER
# define CHIMERA_CHIMERAPATHFINDER

# ifndef CHIMERAPATH_DLL
#  define CHIMERAPATH_IMEX
# elif defined(CHIMERAPATH_EXPORT)
#  define CHIMERAPATH_IMEX __declspec(dllexport)
# else
#  define CHIMERAPATH_IMEX __declspec(dllimport)
# endif

# include <string>
# include <otf/PathFinder.h>

namespace chimera {
	
CHIMERAPATH_IMEX extern void setPathFinder(const std::string &dataRoot,
		const std::string &package, const std::string &env,
		bool hideData = true,
		bool useDotDefault = true, bool useHomeDefault = true);
CHIMERAPATH_IMEX extern const otf::PathFinder *pathFinder();

} // end namespace chimera

# undef CHIMERPATH_IMEX

#endif
