#ifndef chimera_CoordSet_h
#define	chimera_CoordSet_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <vector>
#include <algorithm>
#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "TrackChanges.h"
#include <functional>
#include "Coord.h"
#include "PseudoBondMgr.h"

namespace chimera {
class Molecule;

class CHIMERA_IMEX CoordSet: public otf::WrapPyObj  {
	friend class Molecule;
	void	operator=(const CoordSet &);	// disable
		CoordSet(const CoordSet &);	// disable
		virtual ~CoordSet();
	std::vector<Coord>	Coords_;
	PseudoBondMgr	*PseudoBondMgr_;
public:
	void	addCoord(Coord element);
	void	removeCoord(Coord *element);
	typedef std::vector<Coord> Coords;
	inline const Coords	&coords() const;
	const Coord	*findCoord(int) const;
	Coord	*findCoord(int);
	PseudoBondMgr	*pseudoBondMgr() const;
public:
	inline int		id() const;
	void		fill(const CoordSet *source);
private:
	int	csid;
public:
	virtual PyObject* wpyNew() const;
private:
	static TrackChanges::Changes *const
			changes;
public:
	virtual void	wpyAssociate(PyObject* o) const;

	virtual void	trackReason(const NotifierReason &reason) const;
	struct Reason: public NotifierReason {
                Reason(const char *r): NotifierReason(r) {}
        };
	static Reason		COORD_CHANGED;
private:
	CoordSet(Molecule *, int key);
	CoordSet(Molecule *, int key, int size);
};

} // namespace chimera

#endif
