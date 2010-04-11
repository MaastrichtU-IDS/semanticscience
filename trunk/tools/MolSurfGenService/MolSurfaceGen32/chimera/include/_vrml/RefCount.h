// vi:set ts=4 sw=4:
// --- UCSF Chimera Copyright ---
// Copyright (c) 2000 Regents of the University of California.
// All rights reserved.  This software provided pursuant to a
// license agreement containing restrictions on its disclosure,
// duplication and use.  This notice must be embedded in or
// attached to all copies, including partial copies, of the
// software or any revisions or derivations thereof.
// --- UCSF Chimera Copyright ---
//
// $Id: RefCount.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_REFCOUNT
#define	VRML_REFCOUNT

#include "common.h"

namespace VRML {

class VRML_IMEX RefCount {
private:
	int		refCount_;
public:
			RefCount();
	virtual	~RefCount();
	int		refCount() const;
	void	incRef();
	void	decRef();
};

inline		RefCount::RefCount()
				{
					//std::cerr << "Create reference " << this << '\n';
					refCount_ = 1;
				}
inline		RefCount::~RefCount()
				{
					//std::cerr << "Destroy reference " << this << '\n';
					if (refCount_ > 0)
						std::cerr << "Deleting referenced object\n";
				}
inline int	RefCount::refCount() const
				{
					return refCount_;
				}
inline void	RefCount::incRef()
				{
					//std::cerr << "incref " << this <<' '<< refCount_ << '\n';
					refCount_++;
				}
inline void	RefCount::decRef()
				{
					//std::cerr << "decref " << this <<' '<< refCount_ << '\n';
					if (--refCount_ <= 0)
						delete this;
				}

} // namespace VRML

#endif
