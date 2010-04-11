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
// $Id: BoundingBox.h 26655 2009-01-07 22:02:30Z gregc $

#ifndef VRML_BOUNDINGBOX
#define	VRML_BOUNDINGBOX

#include "common.h"

namespace VRML {

class VRML_IMEX BoundingBox {
protected:
	float			min_[3];
	float			max_[3];
	bool			valid_;
public:
					BoundingBox();
					BoundingBox(const float min[3], const float max[3]);
	const float *	minimum() const;
	const float *	maximum() const;
	bool			valid() const;
	void			addSample(const float sample[3]);
};

inline const float *	BoundingBox::minimum() const { return min_; }
inline const float *	BoundingBox::maximum() const { return max_; }
inline bool				BoundingBox::valid() const { return valid_; }

} // namespace VRML

#endif
