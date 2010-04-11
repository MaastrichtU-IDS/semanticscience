#ifndef Chimera_PdbOrder_h
# define Chimera_PdbOrder_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

#include <vector>
#include <otf/Symbol.h>

namespace chimera {

extern const std::vector<otf::Symbol> &pdbOrder(otf::Symbol resName);

} // namespace chimera

#endif
