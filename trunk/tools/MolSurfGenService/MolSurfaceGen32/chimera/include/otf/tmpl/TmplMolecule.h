#ifndef otf_TmplMolecule_h
#define	otf_TmplMolecule_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <set>
#include <map>
#include <vector>
#include <otf/Symbol.h>
#include <otf/molkit/TAexcept.h>
#include <otf/config.h>
#include "TmplAtom.h"
#include "TmplBond.h"
#include "TmplCoordSet.h"
#include "TmplResidue.h"

namespace otf {

class OTF_IMEX TmplMolecule {
	std::set<TmplAtom *>	Atoms_;
	std::set<TmplBond *>	Bonds_;
	std::map<int, TmplCoordSet *>	CoordSets_;
	std::map<otf::Symbol, TmplResidue *>	Residues_;
public:
		~TmplMolecule();
	TmplAtom	*newAtom(otf::Symbol n, otf::Element e);
	void	deleteAtom(TmplAtom *element);
	typedef std::set<TmplAtom *> Atoms;
	inline const Atoms	&atoms() const;
	TmplBond	*newBond(TmplAtom *a0, TmplAtom *a1);
	TmplBond	*newBond(TmplAtom *a[2]);
	void	deleteBond(TmplBond *element);
	typedef std::set<TmplBond *> Bonds;
	inline const Bonds	&bonds() const;
	TmplCoordSet	*newCoordSet(int key);
	TmplCoordSet	*newCoordSet(int key, int size);
	void	deleteCoordSet(TmplCoordSet *element);
	typedef std::map<int, TmplCoordSet *> CoordSets;
	inline const CoordSets	&coordSets() const;
	TmplCoordSet	*findCoordSet(int) const;
	TmplResidue	*newResidue(otf::Symbol t, otf::MolResId rid);
	TmplResidue	*newResidue(otf::Symbol t, otf::Symbol chain, int pos, char insert);
	void	deleteResidue(TmplResidue *element);
	typedef std::vector<TmplResidue *> Residues;
	inline Residues residues() const;
	typedef std::map<otf::Symbol, TmplResidue *> ResiduesMap;
	inline const ResiduesMap	&residuesMap() const;
	typedef std::vector<otf::Symbol> ResidueKeys;
	inline ResidueKeys	residueNames() const;
	TmplResidue	*findResidue(otf::Symbol) const;
public:
	void		setActiveCoordSet(const TmplCoordSet *a);
	inline TmplCoordSet	*activeCoordSet() const;
private:
	TmplCoordSet	*activeCS;
public:
	TmplMolecule();
};

} // namespace otf

#endif
