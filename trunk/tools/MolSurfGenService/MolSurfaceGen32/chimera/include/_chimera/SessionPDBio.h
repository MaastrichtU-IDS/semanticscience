#ifndef Chimera_SessionPDBio_h
# define Chimera_SessionPDBio_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include "_chimera_config.h"
# include "Mol.h"
# include "PDBio.h"

namespace chimera {

class CHIMERA_IMEX SessionPDBio: public PDBio
{
public:
	SessionPDBio();
	virtual ~SessionPDBio();
#ifdef CHIMERA_64BITPTR
	typedef long sesLong;
#else
	typedef long long sesLong;
#endif
	std::vector<Molecule *> readSessionPDBfile(const char *filename,
				/*OUT*/ std::map<sesLong, Atom *> *sessionIDs);
	std::vector<Molecule *> readSessionPDBstream(std::istream &input,
				const char *filename, /*INOUT*/ int *lineNum,
				/*OUT*/ std::map<sesLong, Atom *> *sessionIDs);
# ifndef WrapPy
	virtual PyObject* wpyNew() const;
# endif
};

} // namespace chimera

#endif
