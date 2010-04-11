#ifndef otf_molkit_PDBioAux_h
# define otf_molkit_PDBioAux_h

# include <otf/config.h>
# include <string>

namespace otf {

OTF_IMEX extern void	PDBioCanonicalizeAtomName(std::string *aname, bool *translated);
OTF_IMEX extern void	PDBioCanonicalizeResidueName(std::string *rname);

} // namespace otf

#endif
