#ifndef otf_OTFPathFinder_h
# define otf_OTFPathFinder_h

# include "config.h"
# include <string>

namespace otf {

class PathFinder;

OTF_IMEX void setOTFPathFinder(const std::string &dataRoot,
		const std::string &package, const std::string &env,
		bool hideData = true,
		bool useDotDefault = true, bool useHomeDefault = true);
OTF_IMEX const PathFinder *OTFPathFinder();

} // namespace otf

#endif
