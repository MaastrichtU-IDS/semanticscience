// Copyright (c) 1996 The Regents of the University of California.
// All rights reserved.
// 
// Redistribution and use in source and binary forms are permitted
// provided that the above copyright notice and this paragraph are
// duplicated in all such forms and that any documentation,
// distribution and/or use acknowledge that the software was developed
// by the Computer Graphics Laboratory, University of California,
// San Francisco.  The name of the University may not be used to
// endorse or promote products derived from this software without
// specific prior written permission.
// 
// THIS SOFTWARE IS PROVIDED ``AS IS'' AND WITHOUT ANY EXPRESS OR
// IMPLIED WARRANTIES, INCLUDING, WITHOUT LIMITATION, THE IMPLIED
// WARRANTIES OF MERCHANTIBILITY AND FITNESS FOR A PARTICULAR PURPOSE.
// IN NO EVENT SHALL THE REGENTS OF THE UNIVERSITY OF CALIFORNIA BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY,
// OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OF THIS SOFTWARE.

// $Id: MolCoordSetId.h 26655 2009-01-07 22:02:30Z gregc $

// coordinate set identifiers

#ifndef MolCoordSetId_h
# define MolCoordSetId_h

# include <otfmisc/Symbol.h>

namespace otf {

class MolCoordSetId {
	Symbol	name_;			/* run/trajectory name */
	int	pos;			/* position */
public:
		MolCoordSetId(): name_(), pos(0) {}
		MolCoordSetId(Symbol n, int pos = 0): name_(n), pos(pos) {}
	Symbol	name() const { return name_; }
	int	position() const { return pos; }
	std::string
		str() const;
	int	sameChain(const MolCoordSetId &id) const {
			return name_ == id.name_;
		}
	int	operator<(const MolCoordSetId &id) const;
	int	operator<=(const MolCoordSetId &id) const;
	int	operator>(const MolCoordSetId &id) const;
	int	operator>=(const MolCoordSetId &id) const;
	int	operator==(const MolCoordSetId &id) const;
	int	operator!=(const MolCoordSetId &id) const;
};

inline int
MolCoordSetId::operator<(const MolCoordSetId &id) const
{
	return (name_ < id.name_ || pos < id.pos);
}

inline int
MolCoordSetId::operator<=(const MolCoordSetId &id) const
{
	return !(name_ > id.name_ || pos > id.pos);
}

inline int
MolCoordSetId::operator>(const MolCoordSetId &id) const
{
	return (name_ > id.name_ || pos > id.pos);
}

inline int
MolCoordSetId::operator>=(const MolCoordSetId &id) const
{
	return !(name_ < id.name_ || pos < id.pos);
}

inline int
MolCoordSetId::operator==(const MolCoordSetId &id) const
{
	return name_ == id.name_ && pos == id.pos;
}

inline int
MolCoordSetId::operator!=(const MolCoordSetId &id) const
{
	return name_ != id.name_ || pos != id.pos;
}

inline std::ostream &
operator<<(std::ostream &os, const MolCoordSetId &id)
{
	os << id.str();
	return os;
}

} // namespace otf

#endif /* MolCoordSetId_h */
