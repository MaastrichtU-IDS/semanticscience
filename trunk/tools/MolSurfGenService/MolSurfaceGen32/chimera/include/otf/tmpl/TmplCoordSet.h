#ifndef otf_TmplCoordSet_h
#define	otf_TmplCoordSet_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <vector>
#include <algorithm>
#include <otf/molkit/TAexcept.h>
#include <otf/config.h>
#include <functional>
#include "TmplCoord.h"

namespace otf {
class TmplMolecule;

class OTF_IMEX TmplCoordSet {
	friend class TmplMolecule;
	void	operator=(const TmplCoordSet &);	// disable
		TmplCoordSet(const TmplCoordSet &);	// disable
		~TmplCoordSet();
	std::vector<TmplCoord>	Coords_;
public:
	void	addCoord(TmplCoord element);
	void	removeCoord(TmplCoord *element);
	typedef std::vector<TmplCoord> Coords;
	inline const Coords	&coords() const;
	const TmplCoord	*findCoord(int) const;
	TmplCoord	*findCoord(int);
public:
	inline int		id() const;
	void		fill(const TmplCoordSet *source);
private:
	int	csid;
private:
	TmplCoordSet(TmplMolecule *, int key);
	TmplCoordSet(TmplMolecule *, int key, int size);
};

} // namespace otf

#endif
