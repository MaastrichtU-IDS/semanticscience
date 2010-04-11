#ifndef chimera_Mol2io_h
#define	chimera_Mol2io_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <iostream>
#include <vector>
#include <map>
#include "Mol2ioHelper.h"
#include <set>
#include <sstream>
#include <iostream>
#include <map>
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include <functional>

namespace chimera {

class CHIMERA_IMEX Mol2io: public otf::WrapPyObj  {
public:
		virtual ~Mol2io();
public:
	std::vector<Molecule *> readMol2stream(std::istream &, const char *, int);
	std::vector<Molecule *> readMol2file(const char *filename);
	void		writeMol2stream(const std::vector<const Molecule *> &, std::ostream &, const char *filename);
	void		writeMol2file(const std::vector<const Molecule *> &, const char *filename);
	inline bool		ok();
	inline std::string	error();

	void		addAtomWithId(int id, Atom *a);
	inline Atom		*atomWithId(int id) const;
	inline void		clearAtomIdMap();
	inline void		addAtomToSubst(int substId, const std::string &name, Atom *a);
	inline std::vector<Atom *>
			extractAtomsInSubst(int substId);
	inline std::string &	substIdToName(int);
	inline std::vector<int>
			substIds();
	inline void		clearSAMap();

	static bool	isBlankLine(const std::string &s);
	static std::vector<std::string>
			splitLine(const std::string &s);
private:
	typedef std::map<int, std::vector<Atom *>, std::less<int> > SAMap;
	typedef std::map<int, std::string> SNMap;

	Mol2ioHelper	*helper;
	std::string	ioErr;
	std::map<int, Atom *, std::less<int> > asn;	// Atom ID -> Atom*
	SAMap		sam;	// residue id -> atom list
	SNMap		snm;	// residue id -> res name (fallback
				//    for missing SUBSTRUCTURE)
public:
	virtual PyObject* wpyNew() const;
private:
	Mol2io(const Mol2io&);			// disable
	Mol2io& operator=(const Mol2io&);	// disable
public:
	Mol2io(Mol2ioHelper *h);
};

} // namespace chimera

#endif
